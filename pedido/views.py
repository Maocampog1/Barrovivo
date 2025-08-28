from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class CarritoDetalleView(TemplateView):
    """Vista básica del carrito: por ahora solo renderiza un template vacío."""
    template_name = "carrito_detalle.html"

