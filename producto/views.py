# Autor: Maria Alejandra Ocampo
from django.views.generic import ListView, DetailView
from .models import Producto

class InicioProductosView(ListView):
    """Catálogo en /producto/: lista productos visibles con stock."""
    template_name = "producto/home.html"
    context_object_name = "productos"

    def get_queryset(self):
        return (Producto.objects
                .filter(es_activo=True, cantidad_disp__gt=0)
                .order_by("nombre"))

class ProductoDetalleView(DetailView):
    model = Producto
    template_name = "detalle.html"
    context_object_name = "producto"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        stock = int(self.object.cantidad_disp or 0)
        # cantidad solicitada por URL ?q=N
        try:
            requested = int(self.request.GET.get("q", 1))
        except (TypeError, ValueError):
            requested = 1

        if stock < 0:
            cantidad = 0
            sin_stock = True
            excedido = False
            al_tope = True
        else:
            if requested < 1:
                requested = 1
            excedido = requested > stock        # <-- SOLO si intenta pasar del stock
            cantidad = min(requested, stock)    # mostramos hasta el tope
            sin_stock = False
            al_tope = (cantidad >= stock)

        ctx.update({
            "cantidad": cantidad,
            "stock": stock,
            "sin_stock": sin_stock,
            "al_tope": al_tope,       # para deshabilitar el botón +
            "excedido": excedido,     # para mostrar el aviso SOLO si se pasó
        })
        return ctx