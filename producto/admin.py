from django.contrib import admin
from .models import Producto, Categoria

# Autor: Maria Alejandra Ocampo
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "cantidad_disp", "es_activo")
    list_filter = ("es_activo", "categorias")
    search_fields = ("nombre", "descripcion")
    filter_horizontal = ("categorias",)  # UI cómoda para ManyToMany
