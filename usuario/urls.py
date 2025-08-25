from django.urls import path
from .views import InicioView, IniciarSesionView, CerrarSesionView, PerfilView

app_name = 'usuario'

urlpatterns = [
    path('', InicioView.as_view(), name='home'),

    # Autenticación
    path('login/', IniciarSesionView.as_view(), name='login'),
    path('logout/', CerrarSesionView.as_view(), name='logout'),

    # Perfil (requiere login)
    path('perfil/', PerfilView.as_view(), name='perfil'),
]
