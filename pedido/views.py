from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView
from .forms import FormularioFacturacion, FormularioEnvio, FormularioPago
from django.template.loader import render_to_string
from django.http import HttpResponse
from decimal import Decimal

from .models import Carrito, ItemCarrito
from producto.models import Producto

# Autor: Luis Angel Nerio   

class CarritoMixin(LoginRequiredMixin):
    """Mixin para obtener/crear el carrito del usuario."""
    def get_carrito(self):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito


class CarritoDetalleView(CarritoMixin, TemplateView):
    """Vista para mostrar el detalle del carrito de compras."""
    template_name = "carrito_detalle.html"   # ajusta si tu template vive en otra carpeta

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        carrito = self.get_carrito()
        ctx["carrito"] = carrito
        ctx["items"] = carrito.items.all()
        ctx["total"] = carrito.obtener_total()
        return ctx


class AgregarAlCarritoView(CarritoMixin, View):
    """POST: agregar un producto al carrito."""
    def post(self, request, producto_id, *args, **kwargs):
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get("cantidad", 1))

        carrito = self.get_carrito()
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={"cantidad": cantidad},
        )
        if not created:
            item.cantidad += cantidad
            item.save()

        messages.success(request, f"{producto.nombre} agregado al carrito.")
        next_url = request.POST.get("next") or reverse("pedido:carrito")
        return redirect(next_url)

    # Si alguien entra por GET, lo redirigimos al detalle del producto (o al carrito).
    def get(self, request, producto_id, *args, **kwargs):
        try:
            return redirect("producto:detalle", pk=producto_id)
        except Exception:
            return redirect("pedido:carrito")


class ActualizarCantidadView(CarritoMixin, View):
    """POST: actualizar la cantidad de un item."""
    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        nueva = int(request.POST.get("cantidad", 1))

        if nueva > 0:
            item.cantidad = nueva
            item.save()
            messages.success(request, "Cantidad actualizada.")
        else:
            item.delete()
            messages.success(request, "Producto removido del carrito.")

        return redirect("pedido:carrito")

    def get(self, request, item_id, *args, **kwargs):
        return redirect("pedido:carrito")


class RemoverDelCarritoView(CarritoMixin, View):
    """POST/GET: remover un item del carrito."""
    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        nombre = item.producto.nombre
        item.delete()
        messages.success(request, f"{nombre} removido del carrito.")
        return redirect("pedido:carrito")

    def get(self, request, item_id, *args, **kwargs):
        return self.post(request, item_id, *args, **kwargs)


class CheckoutView(TemplateView):
    """
    Página de checkout:
    - GET: muestra formularios + resumen del carrito
    - POST: valida, guarda la compra en sesión, vacía el carrito y redirige a /pedido/gracias/
    """
    template_name = "checkout.html"

    # --- helpers ---
    def get_carrito(self):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito

    def _items_carrito(self, carrito):
        """Trae los ítems sin depender de la relación inversa (evita itemcarrito_set)."""
        return ItemCarrito.objects.filter(carrito=carrito)

    # --- GET ---
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        carrito = self.get_carrito()
        items = self._items_carrito(carrito)
        ctx.update({
            "form_facturacion": FormularioFacturacion(),
            "form_envio": FormularioEnvio(),
            "form_pago": FormularioPago(),
            "items": items,
            "total": carrito.obtener_total(),
        })
        return ctx

    # --- POST ---
    def post(self, request, *args, **kwargs):
        f_fact = FormularioFacturacion(request.POST)
        f_env  = FormularioEnvio(request.POST)
        f_pago = FormularioPago(request.POST)

        # Si hay errores, re-pintamos con los datos del carrito
        if not (f_fact.is_valid() and f_env.is_valid() and f_pago.is_valid()):
            carrito = self.get_carrito()
            return self.render_to_response({
                "form_facturacion": f_fact,
                "form_envio": f_env,
                "form_pago": f_pago,
                "items": self._items_carrito(carrito),
                "total": carrito.obtener_total(),
            })

        # Pago simulado OK → construir "compra" desde el carrito y guardar en sesión
        carrito = self.get_carrito()
        items_qs = self._items_carrito(carrito)

        def _to_float(val):
            return float(val) if isinstance(val, Decimal) else val

        lineas = []
        for it in items_qs:
            precio_unit = getattr(it, "precio_unitario", getattr(it.producto, "precio", 0))
            # Usar método subtotal() solo si es callable; si es un campo Decimal, tómalo directo; si no, calcula
            _subtotal_attr = getattr(it, "subtotal", None)
            if callable(_subtotal_attr):
                subtotal = _subtotal_attr()
            elif _subtotal_attr is not None:
                subtotal = _subtotal_attr
            else:
                subtotal = it.cantidad * precio_unit
            lineas.append({
                "nombre": getattr(it.producto, "nombre", str(it.producto)),
                "cantidad": it.cantidad,
                "precio_unitario": _to_float(precio_unit),
                "subtotal": _to_float(subtotal),
            })

        # Calcular total desde las líneas para no depender del estado del carrito
        try:
            computed_total = sum(l["subtotal"] for l in lineas)
        except Exception:
            computed_total = 0

        compra = {
            "numero": timezone.now().strftime("%y%m%d%H%M%S"),   # consecutivo simple
            "creado": timezone.now().strftime("%d/%m/%Y"),
            "total": _to_float(computed_total),
            "facturacion": {
                "correo": f_fact.cleaned_data["correo"],
                "nombres": f_fact.cleaned_data["nombres"],
                "apellidos": f_fact.cleaned_data["apellidos"],
                "cedula": f_fact.cleaned_data["cedula"],
                "telefono": f_env.cleaned_data["telefono"],
            },
            "envio": {
                "departamento": f_env.cleaned_data["departamento"],
                "municipio": f_env.cleaned_data["municipio"],
                "direccion": f_env.cleaned_data["direccion"],
                "apto_info": f_env.cleaned_data.get("apto_info", ""),
            },
            "pago": {
                "metodo": f_pago.cleaned_data["metodo"],
                "nombre_en_tarjeta": f_pago.cleaned_data["nombre_en_tarjeta"],
            },
            "lineas": lineas,
        }

        # Guardar compra en sesión y vaciar carrito
        request.session["ultima_compra"] = compra
        request.session.modified = True

        # Si tu modelo Carrito tiene .vaciar(), úsalo. Si no, borra los ítems manualmente.
        if hasattr(carrito, "vaciar"):
            carrito.vaciar()
        else:
            self._items_carrito(carrito).delete()

        # Redirigir a /pedido/gracias/
        return redirect("pedido:gracias")


class GraciasView(TemplateView):
    template_name = "gracias.html"
    def get(self, request, *args, **kwargs):
        if "ultima_compra" not in request.session:
            return HttpResponseRedirect("/")
        return super().get(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["compra"] = self.request.session.get("ultima_compra", {})
        # Detectar si la generación de PDF está disponible en este entorno
        try:
            from weasyprint import HTML  # noqa: F401
            ctx["pdf_disponible"] = True
        except Exception:
            ctx["pdf_disponible"] = False
        return ctx


class FacturaPDFView(View):
    template_name = "factura_pdf.html"
    def get(self, request):
        compra = request.session.get("ultima_compra")
        if not compra:
            return HttpResponseRedirect("/")
        # Importar WeasyPrint aquí para evitar que el servidor falle si faltan dependencias
        try:
            from weasyprint import HTML
        except Exception as e:
            messages.error(request, "Generación de PDF no disponible: faltan dependencias de WeasyPrint.")
            # Mantener al usuario en la página de gracias para que vea el mensaje
            return redirect("pedido:gracias")

        html = render_to_string(self.template_name, {"compra": compra})
        pdf = HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="factura_{compra["numero"]}.pdf"'
        return resp


class FacturaHTMLView(TemplateView):
    """Fallback imprimible en HTML para guardar como PDF desde el navegador."""
    template_name = "factura_html.html"

    def get(self, request, *args, **kwargs):
        if "ultima_compra" not in request.session:
            return HttpResponseRedirect("/")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["compra"] = self.request.session.get("ultima_compra")
        return ctx
