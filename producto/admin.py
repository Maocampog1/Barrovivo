from django.contrib import admin
from .models import Producto, Categoria, Favorito

# Autor: Maria Alejandra Ocampo
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'cantidad_disp', 'es_activo', 'creado']
    list_filter = ['es_activo', 'categorias', 'creado']
    search_fields = ['nombre', 'descripcion']
    filter_horizontal = ['categorias']
    readonly_fields = ['creado', 'actualizado']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug']
    search_fields = ['nombre']
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'fecha_agregado']
    list_filter = ['fecha_agregado']
    search_fields = ['usuario__username', 'producto__nombre']
    readonly_fields = ['fecha_agregado']
