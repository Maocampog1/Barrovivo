# Autor: Maria Alejandra Ocampo
from decimal import Decimal, InvalidOperation
from django.views.generic import TemplateView
from producto.models import Producto, Categoria

class InicioView(TemplateView):
    """Home: lista de productos con filtros por categoría y precio."""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        qs = Producto.objects.filter(es_activo=True, cantidad_disp__gt=0)

        # --- Filtros (GET) ---
        req = self.request.GET

        # Categorías por slug (varios): ?cat=platos&cat=sets
        slugs = req.getlist("cat")
        if slugs:
            qs = qs.filter(categorias__slug__in=slugs).distinct()

        # Precio mínimo/máximo: ?min=10000&max=700000
        def as_decimal(val):
            try:
                return Decimal(val)
            except (InvalidOperation, TypeError):
                return None

        pmin = as_decimal(req.get("min"))
        pmax = as_decimal(req.get("max"))

        if pmin is not None:
            qs = qs.filter(precio__gte=pmin)
        if pmax is not None:
            qs = qs.filter(precio__lte=pmax)

        # Ordenamiento (placeholder: no implementado todavía)
        # dejamos un order_by por nombre para consistencia
        qs = qs.order_by("nombre")

        # --- Contexto para template ---
        ctx["productos"] = qs
        ctx["categorias"] = Categoria.objects.order_by("nombre")
        ctx["cats_seleccionadas"] = set(slugs)
        ctx["precio_min"] = (self.request.GET.get("min") or "")
        ctx["precio_max"] = (self.request.GET.get("max") or "")
        ctx["orden"] = self.request.GET.get("orden", "")
        return ctx
