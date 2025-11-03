from django.urls import path
from .views import (
    CarritoDetalleView,
    AgregarAlCarritoView,
    ActualizarCantidadView,
    RemoverDelCarritoView,
    CheckoutView,
    GraciasView,
    FacturaHTMLView
)

app_name = "pedido"

urlpatterns = [
    path("carrito/", CarritoDetalleView.as_view(), name="carrito"),
    path("carrito_detalle/", CarritoDetalleView.as_view(), name="carrito_detalle"),
    path("agregar/<int:producto_id>/", AgregarAlCarritoView.as_view(), name="agregar_al_carrito"),
    path("actualizar/<int:item_id>/", ActualizarCantidadView.as_view(), name="actualizar_cantidad"),
    path("remover/<int:item_id>/", RemoverDelCarritoView.as_view(), name="remover_del_carrito"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("gracias/", GraciasView.as_view(), name="gracias"),
    path("factura/<int:pk>/", FacturaHTMLView.as_view(), name="factura_html"),
]
