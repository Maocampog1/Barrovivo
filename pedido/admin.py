from django.contrib import admin
from .models import Carrito, ItemCarrito
# Autor: Luis Angel Nerio
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_creacion', 'fecha_actualizacion', 'obtener_cantidad_total', 'obtener_total']
    list_filter = ['fecha_creacion', 'fecha_actualizacion']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def obtener_cantidad_total(self, obj):
        return obj.obtener_cantidad_total()
    obtener_cantidad_total.short_description = 'Cantidad total'
    
    def obtener_total(self, obj):
        return f"${obj.obtener_total():,}"
    obtener_total.short_description = 'Total'

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'carrito', 'cantidad', 'subtotal', 'fecha_agregado']
    list_filter = ['fecha_agregado']
    search_fields = ['producto__nombre', 'carrito__usuario__username']
    readonly_fields = ['fecha_agregado']
    
    def subtotal(self, obj):
        return f"${obj.subtotal:,}"
    subtotal.short_description = 'Subtotal'
