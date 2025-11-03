from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from pedido.models import Pedido

from .services.reportes_interface import ReporteVentasGenerator
from .services.reportes_pdf import PdfReporteVentasGenerator
from .services.reportes_excel import ExcelReporteVentasGenerator

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff  # o superuser si prefieres

class ReportesIndexView(StaffRequiredMixin, TemplateView):
    template_name = "reportes/index.html"

class ReporteVentasPDFView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pedidos = Pedido.objects.prefetch_related("items", "items__producto").order_by("-fecha")
        generator: ReporteVentasGenerator = PdfReporteVentasGenerator()
        data = generator.render(pedidos)
        resp = HttpResponse(data, content_type="application/pdf")
        resp['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'
        return resp

class ReporteVentasExcelView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pedidos = Pedido.objects.prefetch_related("items", "items__producto").order_by("-fecha")
        generator: ReporteVentasGenerator = ExcelReporteVentasGenerator()
        data = generator.render(pedidos)
        resp = HttpResponse(
            data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp['Content-Disposition'] = 'attachment; filename="reporte_ventas.xlsx"'
        return resp
