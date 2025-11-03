# usuario/groq_client.py
import json
import requests
from django.conf import settings

def _headers():
    return {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def _post_chat(messages):
    """
    Llama a GROQ (OpenAI-compatible) con un modelo fijo (settings.GROQ_MODEL).
    """
    payload = {
        "model": settings.GROQ_MODEL,   # <- modelo fijo
        "messages": messages,
        "temperature": 0.2,
    }

    r = requests.post(
        settings.GROQ_API_URL,
        headers=_headers(),
        data=json.dumps(payload),
        timeout=settings.GROQ_TIMEOUT,
    )

    if r.status_code >= 400:
        # Muestra el cuerpo para entender el 400 si algo pasa
        try:
            err = r.json()
        except Exception:
            err = r.text
        raise RuntimeError(f"GROQ {r.status_code}: {err}")

    data = r.json()
    return data["choices"][0]["message"]["content"]

def extract_criteria(user_text: str) -> dict:
    """
    Pide a la IA que devuelva SOLO JSON, sin response_format (algunos modelos lo rechazan).
    """
    messages = [
        {"role": "system", "content": (
            "Eres un parser. RESPONDE EXCLUSIVAMENTE un JSON válido con estas claves: "
            "uso, persona, tipo, color, estilo, rango_precio, palabras_clave. "
            "Si no aplica, usa null. No agregues nada más."
        )},
        {"role": "user", "content": user_text}
    ]
    text = _post_chat(messages)
    # Parseo robusto
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{"); end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        return {"uso": None, "persona": None, "tipo": None, "color": None,
                "estilo": None, "rango_precio": None, "palabras_clave": []}

def write_answer(criteria: dict, products: list) -> str:
    """
    Redacta 1–2 párrafos sobre los productos candidatos (sin inventar).
    """
    messages = [
        {"role": "system", "content": (
            "Eres un asesor de compras de cerámica. Español, breve y claro. "
            "NO inventes productos ni características no listadas."
        )},
        {"role": "user", "content": (
            "Criterios del usuario:\n" + json.dumps(criteria, ensure_ascii=False) +
            "\n\nEstos son los productos candidatos (id, nombre, precio, nota). "
            "Escribe 1-2 párrafos cortos explicando por qué encajan y cierra con una pregunta.\n" +
            json.dumps(products, ensure_ascii=False)
        )}
    ]
    return _post_chat(messages)
