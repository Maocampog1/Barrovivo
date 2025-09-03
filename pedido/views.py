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
from django.db import transaction


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
    """POST: agregar un producto al carrito respetando el stock."""
    def post(self, request, producto_id, *args, **kwargs):
        producto = get_object_or_404(Producto, id=producto_id)
        stock = int(getattr(producto, "cantidad_disp", 0) or 0)
        try:
            cantidad = max(1, int(request.POST.get("cantidad", 1)))
        except (TypeError, ValueError):
            cantidad = 1

        carrito = self.get_carrito()
        item, _ = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={"cantidad": 0},
        )

        actual = int(item.cantidad or 0)
        disponible = max(0, stock - actual)

        if disponible <= 0:
            messages.warning(request, "No hay más unidades disponibles de este producto.")
        else:
            agregar = min(cantidad, disponible)
            item.cantidad = actual + agregar
            item.save()
            if agregar < cantidad:
                messages.warning(request, f"Solo se agregaron {agregar} unidad(es). Límite por stock: {stock}.")
            else:
                messages.success(request, f"{producto.nombre} agregado al carrito.")

        next_url = request.POST.get("next") or reverse("pedido:carrito")
        return redirect(next_url)

    def get(self, request, producto_id, *args, **kwargs):
        try:
            return redirect("producto:detalle", pk=producto_id)
        except Exception:
            return redirect("pedido:carrito")



class ActualizarCantidadView(CarritoMixin, View):
    """POST: actualizar la cantidad de un item respetando el stock."""
    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        stock = int(getattr(item.producto, "cantidad_disp", 0) or 0)

        try:
            nueva = int(request.POST.get("cantidad", 1))
        except (TypeError, ValueError):
            nueva = 1

        if stock <= 0 or nueva <= 0:
            item.delete()
            messages.warning(request, "Producto sin stock o cantidad inválida. Se removió del carrito.")
            return redirect("pedido:carrito")

        if nueva > stock:
            item.cantidad = stock
            item.save()
            messages.warning(request, f"Cantidad ajustada a {stock} por límite de stock.")
        else:
            item.cantidad = nueva
            item.save()
            messages.success(request, "Cantidad actualizada.")

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
    - POST: valida, descuenta stock, guarda la compra en sesión, vacía el carrito y redirige.
    """
    template_name = "checkout.html"

    # --- helpers ---
    def get_carrito(self):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito

    def _items_carrito(self, carrito):
        """Trae los ítems sin depender de la relación inversa (evita itemcarrito_set)."""
        return ItemCarrito.objects.filter(carrito=carrito)

    # --- GET (igual que lo tienes) ---
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

    # --- POST (nuevo con descuento de stock) ---
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

        carrito = self.get_carrito()
        items_qs = self._items_carrito(carrito).select_related("producto").order_by("id")

        # Si no hay ítems, no hay nada que pagar
        if not items_qs.exists():
            messages.warning(request, "Tu carrito está vacío.")
            return redirect("pedido:carrito")

        # Pre-chequeo rápido de stock antes de entrar a la transacción
        for it in items_qs:
            stock = int(getattr(it.producto, "cantidad_disp", 0) or 0)
            if it.cantidad > stock:
                messages.error(
                    request,
                    f"Stock insuficiente para '{it.producto.nombre}'. Disponible: {stock}. Ajusta cantidades."
                )
                return redirect("pedido:carrito")

        def _to_float(val):
            from decimal import Decimal
            return float(val) if isinstance(val, Decimal) else val

        # Transacción: si algo falla, se revierte todo (no se descuenta stock a medias)
        from decimal import Decimal
        lineas = []

        with transaction.atomic():
            # 1) Descontar stock producto a producto
            for it in items_qs:
                prod = it.producto
                try:
                    # Usa el método de dominio que ya tienes en Producto
                    prod.restar_cantidad(it.cantidad)  # valida y guarda cantidad_disp
                except ValueError:
                    transaction.set_rollback(True)
                    messages.error(
                        request,
                        f"Stock insuficiente para '{prod.nombre}'. Disponible: {prod.cantidad_disp}. Ajusta cantidades."
                    )
                    return redirect("pedido:carrito")

            # 2) Construir líneas con los datos finales
            for it in items_qs:
                precio_unit = getattr(it, "precio_unitario", getattr(it.producto, "precio", 0))
                # calcular subtotal con precisión decimal
                if not isinstance(precio_unit, Decimal):
                    precio_unit = Decimal(str(precio_unit))
                subtotal = it.cantidad * precio_unit
                lineas.append({
                    "nombre": getattr(it.producto, "nombre", str(it.producto)),
                    "cantidad": it.cantidad,
                    "precio_unitario": _to_float(precio_unit),
                    "subtotal": _to_float(subtotal),
                })

            computed_total = sum(Decimal(str(l["subtotal"])) for l in lineas)

            # 3) Guardar la compra en sesión
            from django.utils import timezone
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
            request.session["ultima_compra"] = compra
            request.session.modified = True

            # 4) Vaciar carrito
            if hasattr(carrito, "vaciar"):
                carrito.vaciar()
            else:
                items_qs.delete()

        # 5) Ir a la pantalla de gracias (con botón para ver factura)
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
