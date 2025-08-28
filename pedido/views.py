from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from .models import Carrito, ItemCarrito
from producto.models import Producto


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
