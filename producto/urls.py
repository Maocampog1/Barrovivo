from django.urls import path
from django.views.generic import RedirectView
from .views import InicioProductosView

app_name = "producto"

urlpatterns = [
    path("", InicioProductosView.as_view(), name="home"),  # /producto/
    path("favoritos/", RedirectView.as_view(pattern_name="producto:home"), name="favoritos"),
]
