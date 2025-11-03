# usuario/chat_service.py
from typing import List, Optional, Dict, Tuple
from django.db.models import Q
from django.conf import settings
from producto.models import Producto, Categoria
import unicodedata
import re

# =========================
# Normalización básica
# =========================
def _norm(s: Optional[str]) -> Optional[str]:
    """minúsculas + sin acentos + trim."""
    if not s:
        return None
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s

def _tokenize(text: str) -> List[str]:
    """Tokeniza por palabras (solo letras/números), normalizado."""
    t = _norm(text) or ""
    return re.findall(r"[a-z0-9]+", t)

# =========================
# SINÓNIMOS → CATEGORÍA CANÓNICA
# =========================
# Claves canónicas: "matera", "jarron", "pocillo", "plato", "set"
CANON_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
    "matera": {
        "palabras": [
            "matera", "materas", "maceta", "macetas", "matero", "tiesto",
            "florero para plantar", "lugar para colocar plantas", "para plantar",
            "para plantas", "jardinera"
        ],
    },
    "jarron": {
        "palabras": [
            "jarron", "jarrones", "jarron", "jarron", "jarron",  # redundante a propósito tras normalizar
            "jarron", "jarra", "jarras", "vasija", "florero",
            "utensilio para echar agua", "donde echar agua", "echar agua",
            "jarron con flores", "adorno alto"
        ],
    },
    "pocillo": {
        "palabras": [
            "pocillo", "pocillos", "taza", "tazas", "tacita", "tacitas",
            "mug", "mugs", "donde beber agua", "para beber", "para cafe", "para te",
            "vaso pequeno", "vaso", "vasos"
        ],
    },
    "plato": {
        "palabras": [
            "plato", "platos", "platon", "platones",
            "fuente", "fuentes", "bandeja", "bandejas",
            "bandeja ceramica", "bajo plato", "bajo platos", "bandeja para servir"
        ],
    },
    "set": {
        "palabras": ["set", "sets", "juego", "juegos", "kit", "conjunto", "juego de"],
    },
}

# Invertimos a sinónimo -> canónica para matching rápido por palabra
INVERTED: Dict[str, str] = {}
# Además, guardamos SINÓNIMOS multi-palabra (frases) por longitudes (para buscar en texto)
PHRASES: List[Tuple[str, str]] = []  # (frase_normalizada, canon)
for canon, data in CANON_SYNONYMS.items():
    for s in data["palabras"]:
        ns = _norm(s)
        if not ns:
            continue
        if " " in ns:  # frase
            PHRASES.append((ns, canon))
        else:
            INVERTED[ns] = canon
# Ordenamos frases por longitud descendente para evitar solapamientos ("bandeja" vs "bandeja ceramica")
PHRASES.sort(key=lambda x: len(x[0]), reverse=True)

def _first_canon_in_text(text: str) -> Optional[str]:
    """
    Devuelve la canónica según la primera aparición en el texto.
    Primero buscamos frases (multi-palabra), luego palabras tokenizadas.
    """
    nt = _norm(text) or ""

    # 1) Buscar frases en orden de aparición
    earliest = (len(nt) + 1, None)  # (posicion, canon)
    for phrase, canon in PHRASES:
        pos = nt.find(phrase)
        if pos != -1 and pos < earliest[0]:
            earliest = (pos, canon)

    # 2) Si no hubo frases, miramos por tokens
    if earliest[1] is None:
        tokens = _tokenize(text)
        for i, tok in enumerate(tokens):
            canon = INVERTED.get(tok)
            if canon:
                return canon
        return None

    return earliest[1]

def _get_categoria(canon: str) -> Optional[Categoria]:
    """Busca la categoría por slug o nombre aproximado de la canónica (singular/plural y sinónimos)."""
    if not canon:
        return None

    q = Q(slug__icontains=canon) | Q(nombre__icontains=canon)

    # Sumamos sinónimos de esa canónica
    for s in CANON_SYNONYMS.get(canon, {}).get("palabras", []):
        ns = _norm(s)
        if ns:
            q |= Q(slug__icontains=ns) | Q(nombre__icontains=ns)

    return Categoria.objects.filter(q).first()

def _fallback_nombre_contains(qs, canon: str):
    """
    Si no se encontró la categoría M2M, filtramos por nombre/descripcion del producto
    usando los sinónimos de la canónica como fallback estricto.
    """
    syns = CANON_SYNONYMS.get(canon, {}).get("palabras", [])
    q = Q()
    for s in syns:
        ns = _norm(s)
        if not ns:
            continue
        q |= Q(nombre__icontains=ns) | Q(descripcion__icontains=ns)
    return qs.filter(q)

def _img_url(p):
    """
    Devuelve la URL de imagen del producto si existe.
    Intenta campos comunes: imagen, foto, image, portada...
    """
    for attr in ["imagen", "foto", "image", "imagen_principal", "foto_principal", "portada"]:
        f = getattr(p, attr, None)
        if f:
            try:
                return f.url  # MEDIA_URL + nombre
            except Exception:
                pass
    return None

def search_products(criteria: dict, user_text: str, limit: int = 8) -> List[dict]:
    """
    Reglas:
      1) Detecta canónica por 'tipo' del LLM; si no, por el texto del usuario (primera mención).
      2) Filtra SOLO esa categoría (estricto).
      3) Si no localiza categoría M2M, hace fallback por nombre/descr usando los sinónimos.
      4) Filtro suave adicional por color/keywords si vienen del LLM.
    """
    tipo_llm = _norm(criteria.get("tipo"))
    color    = _norm(criteria.get("color"))
    kws      = [_norm(k) for k in (criteria.get("palabras_clave") or []) if _norm(k)]

    # 1) Canónica a partir del tipo del LLM o del texto del usuario
    canon = _first_canon_in_text(tipo_llm or "") or _first_canon_in_text(user_text)
    if not canon:
        # Sin categoría clara: no devolvemos nada (comportamiento estricto que pediste)
        return []

    # 2) Query base
    qs = Producto.objects.filter(es_activo=True, cantidad_disp__gt=0).prefetch_related("categorias").distinct()

    # 3) Intento por categoría real (M2M)
    cat = _get_categoria(canon)
    if cat:
        qs = qs.filter(categorias=cat)
    else:
        # 4) Fallback estricto por texto de producto usando sinónimos de la canónica
        qs = _fallback_nombre_contains(qs, canon)

    # 5) Filtro suave por color/keywords (si existen)
    text_q = Q()
    if color:
        text_q |= Q(nombre__icontains=color) | Q(descripcion__icontains=color)
    for kw in kws:
        text_q |= Q(nombre__icontains=kw) | Q(descripcion__icontains=kw)
    if text_q:
        qs = qs.filter(text_q)

    # 6) Orden y límite
    qs = qs.order_by("precio", "nombre")[:limit]

    # 7) Serialización
    out = []
    for p in qs:
        out.append({
            "id": p.id,
            "nombre": p.nombre,
            "precio": float(p.precio),
            "nota": (p.descripcion or "")[:180],
            "imagen": _img_url(p),
        })
    return out
