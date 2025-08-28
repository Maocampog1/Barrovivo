from django.urls import path
from .views import InicioView, IniciarSesionView, CerrarSesionView, PerfilView, CrearCuentaView

app_name = 'usuario'

urlpatterns = [
    path('', InicioView.as_view(), name='home'),
    path('login/', IniciarSesionView.as_view(), name='login'),
    path('logout/', CerrarSesionView.as_view(), name='logout'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('registro/', CrearCuentaView.as_view(), name='registro'),  # ← nuevo
]
