from django.urls import path
from django.views.generic import RedirectView

app_name = 'producto'

urlpatterns = [
    # nombre requerido por {% url 'producto:favoritos' %} → redirige a home
    path('favoritos/', RedirectView.as_view(pattern_name='usuario:home'), name='favoritos'),
]
