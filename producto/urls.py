from django.urls import path
from django.views.generic import RedirectView
from .views import InicioProductosView, ProductoDetalleView, ToggleFavoritoView, FavoritosView


app_name = 'producto'

urlpatterns = [
    path('', InicioProductosView.as_view(), name='inicio'),
    path('<int:pk>/', ProductoDetalleView.as_view(), name='detalle'),
    path('favoritos/', FavoritosView.as_view(), name='favoritos'),
    path('toggle-favorito/<int:producto_id>/', ToggleFavoritoView.as_view(), name='toggle_favorito'),
]
