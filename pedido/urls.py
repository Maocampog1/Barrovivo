from django.urls import path
from django.views.generic import RedirectView

app_name = 'pedido'

urlpatterns = [
    # nombre requerido por {% url 'pedido:carrito' %} → redirige a home
    path('carrito/', RedirectView.as_view(pattern_name='usuario:home'), name='carrito'),
]
