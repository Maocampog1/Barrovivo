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
from django.utils import timezone
from django.utils.timezone import now
from .models import Carrito, ItemCarrito, Pedido, PedidoItem
from producto.models import Producto

# Autor: Luis Angel Nerio  
# Editado: Camilo Salazar 


class CarritoMixin(LoginRequiredMixin):
    """Mixin para obtener/crear el carrito del usuario."""
    def get_carrito(self):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito


class CarritoDetalleView(CarritoMixin, TemplateView):
    """Vista para mostrar el detalle del carrito de compras."""
    template_name = "carrito_detalle.html"   

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
        f_env = FormularioEnvio(request.POST)
        f_pago = FormularioPago(request.POST)

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
        items_qs = self._items_carrito(carrito).select_related("producto")

        if not items_qs.exists():
            messages.warning(request, "Tu carrito está vacío.")
            return redirect("pedido:carrito")

        #numero_pedido = now().strftime("%y%m%d%H%M%S")
#Editado por Camilo Salazar
        with transaction.atomic():
            # Crear Pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                nombre_cliente=f"{f_fact.cleaned_data['nombres']} {f_fact.cleaned_data['apellidos']}",
                correo=f_fact.cleaned_data["correo"],
                cedula=f_fact.cleaned_data["cedula"],
                celular=f_env.cleaned_data["telefono"],
                departamento=f_env.cleaned_data["departamento"],
                municipio=f_env.cleaned_data["municipio"],
                direccion=f_env.cleaned_data["direccion"],
                apto_info=f_env.cleaned_data.get("apto_info", ""),
                total=carrito.obtener_total(),
            )

            # Crear PedidoItem y descontar stock
            for it in items_qs:
                prod = it.producto
                prod.restar_cantidad(it.cantidad)
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=prod,
                    cantidad=it.cantidad,
                    precio=prod.precio
                )

            carrito.items.all().delete()

        request.session["ultima_compra_id"] = pedido.id
        return redirect("pedido:gracias")


class GraciasView(LoginRequiredMixin, TemplateView):
    template_name = "gracias.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pedido_id = self.request.session.get("ultima_compra_id")
        if not pedido_id:
            raise Http404("No hay pedido registrado")
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=self.request.user)
        ctx["pedido"] = pedido
        return ctx


class FacturaHTMLView(LoginRequiredMixin, TemplateView):
    template_name = "factura_html.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pedido = get_object_or_404(Pedido, id=kwargs.get("pk"), usuario=self.request.user)
        ctx["pedido"] = pedido
        ctx["itemsPedido"] = pedido.items.all()  
        return ctx