# producto/tests.py
from decimal import Decimal
from django.test import TestCase
from .models import Producto


class ProductoTests(TestCase):
    def test_restar_cantidad_disminuye_stock(self):
        # Arrange: creamos un producto con stock 5
        p = Producto.objects.create(
            nombre="Taza de prueba",
            descripcion="Taza para pruebas",
            precio=Decimal("10000.00"),
            cantidad_disp=5,
        )

        # Act: restamos 2 unidades
        p.restar_cantidad(2)
        p.refresh_from_db()

        # Assert: el stock debería quedar en 3
        self.assertEqual(p.cantidad_disp, 3)
