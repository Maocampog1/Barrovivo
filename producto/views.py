# Autor: Maria Alejandra Ocampo
from django.views.generic import ListView
from .models import Producto

class InicioProductosView(ListView):
    """Catálogo en /producto/: lista productos visibles con stock."""
    template_name = "producto/home.html"
    context_object_name = "productos"

    def get_queryset(self):
        return (Producto.objects
                .filter(es_activo=True, cantidad_disp__gt=0)
                .order_by("nombre"))
