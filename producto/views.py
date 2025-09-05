# Autor: Maria Alejandra Ocampo
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Producto, Favorito


class InicioProductosView(ListView):
    """Catálogo en /producto/: lista productos visibles con stock."""
    template_name = "home.html"
    context_object_name = "productos"

    def get_queryset(self):
        return (Producto.objects
                .filter(es_activo=True, cantidad_disp__gt=0)
                .order_by("nombre"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información de favoritos para cada producto
        if self.request.user.is_authenticated:
            favoritos_ids = set(
                Favorito.objects.filter(usuario=self.request.user)
                .values_list('producto_id', flat=True)
            )
            for producto in context['productos']:
                producto.es_favorito = producto.id in favoritos_ids
        return context


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

        # Verificar si el producto está en favoritos
        es_favorito = False
        if self.request.user.is_authenticated:
            es_favorito = Favorito.objects.filter(
                usuario=self.request.user, 
                producto=self.object
            ).exists()

        ctx.update({
            "cantidad": cantidad,
            "stock": stock,
            "sin_stock": sin_stock,
            "al_tope": al_tope,       # para deshabilitar el botón +
            "excedido": excedido,     # para mostrar el aviso SOLO si se pasó
            "es_favorito": es_favorito,
        })
        return ctx
    
#Autor: Luis Angel Nerio


class ToggleFavoritoView(LoginRequiredMixin, View):
    """Añade o quita un producto de favoritos del usuario."""
    def post(self, request, producto_id, *args, **kwargs):
        producto = get_object_or_404(Producto, pk=producto_id)
        favorito, created = Favorito.objects.get_or_create(
            usuario=request.user, 
            producto=producto
        )
        
        if created:
            messages.success(request, f"{producto.nombre} añadido a favoritos.")
        else:
            favorito.delete()
            messages.success(request, f"{producto.nombre} quitado de favoritos.")

        # Volver a donde estaba el usuario
        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        # fallback: detalle del producto
        try:
            return redirect("producto:detalle", pk=producto.id)
        except Exception:
            return redirect("producto:inicio")


class FavoritosView(LoginRequiredMixin, ListView):
    """Vista para mostrar los productos favoritos del usuario."""
    template_name = "favoritos.html"
    context_object_name = "productos"

    def get_queryset(self):
        return Producto.objects.filter(
            favoritos__usuario=self.request.user,
            es_activo=True
        ).order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Marcar todos como favoritos ya que están en esta vista
        for producto in context['productos']:
            producto.es_favorito = True
        return context