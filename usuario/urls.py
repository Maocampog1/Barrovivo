from django.urls import path
from .views import InicioView
from django.views.generic import RedirectView

app_name = 'usuario'

urlpatterns = [
    path('', InicioView.as_view(), name='home'),
    # Solo nombres para que el {% url %} no rompa; redirigen a home
    path('perfil/', RedirectView.as_view(pattern_name='usuario:home'), name='perfil'),
    path('logout/', RedirectView.as_view(pattern_name='usuario:home'), name='logout'),
]
