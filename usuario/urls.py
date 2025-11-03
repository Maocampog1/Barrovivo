from django.urls import path
from .views import InicioView, IniciarSesionView, CerrarSesionView, PerfilView, CrearCuentaView, chat_api, AsistenteView 
from .views_reportes import (
    ReportesIndexView, ReporteVentasPDFView, ReporteVentasExcelView
)
app_name = 'usuario'

urlpatterns = [
    path('', InicioView.as_view(), name='home'),
    path('login/', IniciarSesionView.as_view(), name='login'),
    path('logout/', CerrarSesionView.as_view(), name='logout'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('registro/', CrearCuentaView.as_view(), name='registro'),
    path('api/chat/', chat_api, name='chat_api'),
    path('asistente/', AsistenteView.as_view(), name='asistente'),

    # --- Reportes solo para admin/staff ---
    path("reportes/", ReportesIndexView.as_view(), name="reportes_index"),
    path("reportes/ventas/pdf/", ReporteVentasPDFView.as_view(), name="reporte_ventas_pdf"),
    path("reportes/ventas/excel/", ReporteVentasExcelView.as_view(), name="reporte_ventas_excel"),
]
