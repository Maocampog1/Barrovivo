from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # ←  para /i18n/setlang/
    path('admin/', admin.site.urls),
    path('', include('usuario.urls')),        # ← La HOME sigue siendo la de usuario
    path('producto/', include('producto.urls')),  # Catálogo en /producto/
    path('pedido/', include('pedido.urls')),      # Carrito/Checkout en /pedido/
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
