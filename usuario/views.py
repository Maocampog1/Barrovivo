# Autor: Maria Alejandra Ocampo
# Editado: Camilo Salazr
from decimal import Decimal, InvalidOperation

from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.db.models.functions import Coalesce
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib import messages
from .forms import CrearCuentaForm
from pedido.models import Pedido
from producto.models import Producto, Categoria, Favorito

import json
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .groq_client import extract_criteria, write_answer
from .chat_service import search_products



# Autor: Maria Alejandra Ocampo
# Editado: Camilo Salazar
from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib import messages
from .forms import CrearCuentaForm
from pedido.models import Pedido
from producto.models import Producto, Categoria, Favorito


class InicioView(TemplateView):
    """Home: lista de productos con filtros por categoría, precio y ventas."""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        req = self.request.GET

        productos = Producto.objects.filter(es_activo=True, cantidad_disp__gt=0)

        # --- Filtros ---
        # Categorías seleccionadas (?cat=platos&cat=sets)
        slugs = req.getlist("cat")
        if slugs:
            productos = productos.filter(categorias__slug__in=slugs).distinct()

        # Precio
        def to_decimal(val):
            try:
                return Decimal(val)
            except (InvalidOperation, TypeError):
                return None

        pmin = to_decimal(req.get("min"))
        pmax = to_decimal(req.get("max"))
        if pmin is not None:
            productos = productos.filter(precio__gte=pmin)
        if pmax is not None:
            productos = productos.filter(precio__lte=pmax)

        # --- Anotar ventas ---
        productos = productos.annotate(
            ventas=Coalesce(Sum("pedidoitem__cantidad"), 0)
        )

        # --- Ordenar ---
        orden = req.get("orden", "")
        if orden == "mas":
            productos = productos.order_by("-ventas", "-id")
        elif orden == "menos":
            productos = productos.order_by("ventas", "-id")
        else:
            productos = productos.order_by("-id")

        # --- Marcar favoritos ---
        if self.request.user.is_authenticated:
            fav_ids = set(
                Favorito.objects.filter(usuario=self.request.user)
                .values_list("producto_id", flat=True)
            )
            for p in productos:
                p.es_favorito = p.id in fav_ids

        # --- Contexto ---
        ctx.update({
            "productos": productos,
            "categorias": Categoria.objects.order_by("nombre"),
            "cats_seleccionadas": set(slugs),
            "precio_min": req.get("min", ""),
            "precio_max": req.get("max", ""),
            "orden": orden,
        })
        return ctx
    
    
class IniciarSesionView(LoginView):
    """Pantalla de login con plantilla propia."""
    template_name = 'login.html'
    redirect_authenticated_user = True  # si ya está logueado, envía al home

    def get_success_url(self):
        # respeta ?next=..., si no hay, vuelve al home
        return self.get_redirect_url() or reverse_lazy('usuario:home')


class CerrarSesionView(LogoutView):
    """Cierra sesión y redirige al home."""
    next_page = reverse_lazy('usuario:home')


class PerfilView(LoginRequiredMixin, TemplateView):
    """Página de perfil (solo autenticados)."""
    template_name = 'perfil.html'
    login_url = reverse_lazy('usuario:login')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pedidos = Pedido.objects.filter(usuario=self.request.user).order_by('-fecha')
        ctx["pedidos"] = pedidos
        return ctx


class CrearCuentaView(FormView):
    """Crear cuenta (registro)."""
    template_name = 'registro.html'
    form_class = CrearCuentaForm
    success_url = reverse_lazy('usuario:login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Cuenta creada. Ahora puedes iniciar sesión.")
        return super().form_valid(form)
    
class AsistenteView(TemplateView):
    template_name = "asistente.html"  # o "usuario/asistente.html" según tu ruta


@csrf_exempt
@require_POST
def chat_api(request: HttpRequest):
    """
    POST: { "message": "texto del usuario" }
    RESP: { ok, text, products[] }
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    user_text = (payload.get("message") or "").strip()
    if not user_text:
        return JsonResponse({"error": "Falta 'message'"}, status=400)

    try:
        criteria = extract_criteria(user_text)          # 1) GROQ parse
        products = search_products(criteria, user_text, limit=8)  # 2) BD con sinónimos
        answer = write_answer(criteria, products)       # 3) GROQ redacción
        return JsonResponse({"ok": True, "text": answer, "products": products})
    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"ok": False, "error": str(e)}, status=500)