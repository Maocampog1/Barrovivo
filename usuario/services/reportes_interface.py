from abc import ABC, abstractmethod
from typing import Iterable, Protocol, Any

class ReporteVentasGenerator(ABC):
    """Interfaz DIP para generadores de reportes de ventas."""
    @abstractmethod
    def render(self, pedidos: Iterable[Any]) -> bytes:
        ...

class HasNombreArchivo(Protocol):
    @property
    def filename(self) -> str: ...
