from django.db import models
from django.contrib.auth.models import User
from producto.models import Producto

# Create your models here.

class Carrito(models.Model):
    """Modelo para representar el carrito de compras de un usuario."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def obtener_total(self):
        """Calcula el total del carrito."""
        return sum(item.subtotal for item in self.items.all())
    
    def obtener_cantidad_total(self):
        """Calcula la cantidad total de items en el carrito."""
        return sum(item.cantidad for item in self.items.all())

class ItemCarrito(models.Model):
    """Modelo para representar un item individual en el carrito."""
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['carrito', 'producto']
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en carrito de {self.carrito.usuario.username}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal de este item."""
        return self.producto.precio * self.cantidad
    

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    nombre_cliente = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20)
    celular = models.CharField(max_length=20)
    correo = models.EmailField()
    departamento = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    apto_info = models.CharField(max_length=100, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    
    def __str__(self):
        return f"Pedido {self.id} de {self.usuario.username}"
    


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
