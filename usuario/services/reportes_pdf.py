# usuario/services/reportes_pdf.py
from typing import Iterable, Any
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from .reportes_interface import ReporteVentasGenerator

class PdfReporteVentasGenerator(ReporteVentasGenerator):
    filename = "reporte_ventas.pdf"

    def render(self, pedidos: Iterable[Any]) -> bytes:
        """
        Genera un PDF a partir del template HTML usando xhtml2pdf (puro Python).
        Evitamos dependencias del sistema (GTK/Pango) que requiere WeasyPrint.
        """
        # Asegúrate de que el template exista en esta ruta:
        # usuario/templates/usuario/reportes/ventas_pdf.html
        html = render_to_string("reportes/ventas_pdf.html", {
            "pedidos": pedidos,
        })

        buf = BytesIO()
        # encoding='utf-8' para caracteres acentuados
        pisa_status = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
        if pisa_status.err:
            # En caso de error, devuelve PDF vacío (o lanza excepción si prefieres)
            return b""
        return buf.getvalue()
