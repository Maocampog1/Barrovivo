from django.urls import path
from django.views.generic import RedirectView
from .views import InicioProductosView, ProductoDetalleView


app_name = 'producto'

urlpatterns = [
    path('', InicioProductosView.as_view(), name='inicio'),
    path('<int:pk>/', ProductoDetalleView.as_view(), name='detalle'),
    path('favoritos/', RedirectView.as_view(pattern_name='usuario:home'), name='favoritos'),
]
