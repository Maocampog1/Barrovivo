from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Autor: Maria Alejandra Ocampo
class Categoria(models.Model):
    """Catálogo de categorías (Materas, Jarrones, Platos, Sets, Pocillos, ...)."""
    nombre = models.CharField(max_length=80, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=90, unique=True, verbose_name="Slug", blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        return super().save(*args, **kwargs)


class Producto(models.Model):
    """Entidad de dominio para los productos del catálogo."""
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    categorias = models.ManyToManyField(Categoria, related_name="productos", blank=True, verbose_name="Categorías")

    precio = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio")
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True, verbose_name="Imagen")
    cantidad_disp = models.PositiveIntegerField(default=0, verbose_name="Cantidad disponible")
    es_activo = models.BooleanField(default=True, verbose_name="Visible")

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre

    # ——— Métodos de dominio mínimos ———
    def restar_cantidad(self, cantidad: int = 1) -> None:
        """Resta stock disponible. Lanza ValueError si no alcanza."""
        if cantidad < 0:
            raise ValueError("La cantidad a restar debe ser positiva.")
        if self.cantidad_disp < cantidad:
            raise ValueError("No hay stock suficiente.")
        self.cantidad_disp -= cantidad
        self.save(update_fields=["cantidad_disp"])

    def anadir_cantidad(self, cantidad: int = 1) -> None:
        """Incrementa stock disponible."""
        if cantidad < 0:
            raise ValueError("La cantidad a añadir debe ser positiva.")
        self.cantidad_disp += cantidad
        self.save(update_fields=["cantidad_disp"])

#Autor: Luis Angel Nerio
class Favorito(models.Model):
    """Modelo para los productos favoritos de los usuarios."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favoritos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="favoritos")
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'producto']
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"

    def __str__(self):
        return f"{self.usuario}  {self.producto}"
