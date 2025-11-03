from django.contrib import admin
from .models import Carrito, ItemCarrito, Pedido, PedidoItem

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


# Inline para mostrar los items dentro de Pedido
class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio')
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'correo', 'fecha',  'total')
    list_filter = ('fecha', 'departamento', 'municipio')
    search_fields = ('usuario__username', 'nombre_cliente', 'correo', 'cedula')
    readonly_fields = ('fecha',)
    inlines = [PedidoItemInline]


@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio')
    search_fields = ('producto__nombre',)
    list_filter = ('pedido__fecha',)
