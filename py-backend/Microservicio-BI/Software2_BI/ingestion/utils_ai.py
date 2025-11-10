# ingestion/utils_ai.py

import json
import re


def _extract_json_block(raw_text: str) -> str | None:
    """
    Extrae el primer bloque JSON válido de un texto generado por la IA.

    Soporta casos donde el modelo envuelve la respuesta así:

        ```json
        { "tabla": "producto", "sql": "SELECT ..." }
        ```

    o mezcla texto antes/después.
    """
    if not raw_text:
        return None

    # Si viene en bloque ```json ... ```
    fenced = re.search(r"```json(.*?)```", raw_text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    # Buscar primer posible JSON { ... }
    curly_match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
    if curly_match:
        try:
            json.loads(curly_match.group(0))
            return curly_match.group(0)
        except Exception:
            pass

    return None
