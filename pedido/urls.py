from django.urls import path
from django.views.generic import RedirectView
from .views import CarritoDetalleView

app_name = 'pedido'

urlpatterns = [
    # nombre requerido por {% url 'pedido:carrito' %} → redirige a home
    path('carrito/', CarritoDetalleView.as_view(), name='carrito'),
    path('carrito_detalle/', CarritoDetalleView.as_view(), name='carrito_detalle'),
]
