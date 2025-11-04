# pedido/tests.py
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from producto.models import Producto
from .models import Carrito, ItemCarrito


class CarritoTests(TestCase):
    def test_obtener_total_y_cantidad_total(self):
        # Arrange: usuario, producto y carrito
        usuario = User.objects.create_user(username="cliente@test.com", password="12345678")

        producto = Producto.objects.create(
            nombre="Plato de prueba",
            descripcion="Plato para pruebas",
            precio=Decimal("15000.00"),
            cantidad_disp=10,
        )

        carrito = Carrito.objects.create(usuario=usuario)

        # Agregamos 2 unidades al carrito
        ItemCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            cantidad=2,
        )

        # Act
        total = carrito.obtener_total()
        cantidad_total = carrito.obtener_cantidad_total()

        # Assert
        self.assertEqual(cantidad_total, 2)
        self.assertEqual(total, producto.precio * 2)
