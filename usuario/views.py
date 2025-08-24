# Autor: Maria Alejandra Ocampo
from django.views.generic import TemplateView
from producto.models import Producto

class InicioView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["productos"] = (Producto.objects
                            .filter(es_activo=True, cantidad_disp__gt=0)
                            .order_by("nombre"))
        return ctx
