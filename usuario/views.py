from django.shortcuts import render

# Create your views here.
# Autor: Maria Alejandra Ocampo
from django.views.generic import TemplateView

class InicioView(TemplateView):
    template_name = 'home.html'
