"""Descarga los textos oficiales del AI Act y RGPD desde EUR-Lex.

Los textos se guardan en data/raw/ como HTML. La extraccion estructurada
por articulos se hace en un paso posterior (parse_norms.py).

Nota: EUR-Lex devuelve 202 (vacio) si el User-Agent parece un bot.
Se usa un UA de navegador real y requests.Session para que las cookies
de sesion persistan entre reintentos.
"""

from __future__ import annotations

import time
from pathlib import Path

import requests
from loguru import logger

# URLs oficiales de EUR-Lex en espanol
SOURCES = {
    "ai_act.html": "https://eur-lex.europa.eu/legal-content/ES/TXT/HTML/?uri=CELEX:32024R1689",
    "rgpd.html": "https://eur-lex.europa.eu/legal-content/ES/TXT/HTML/?uri=CELEX:32016R0679",
}

OUT_DIR = Path("data/raw")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}
_MIN_BYTES = 10_000  # un HTML real pesa mucho mas que esto
_MAX_RETRIES = 4
_RETRY_DELAY = 4  # segundos entre reintentos (EUR-Lex puede tardar en generar)


def _fetch_with_retry(session: requests.Session, url: str) -> bytes:
    for attempt in range(1, _MAX_RETRIES + 1):
        r = session.get(url, timeout=60)
        r.raise_for_status()
        if len(r.content) >= _MIN_BYTES:
            return r.content
        logger.warning(
            f"Respuesta vacia/incompleta ({len(r.content)} bytes, status {r.status_code}), "
            f"intento {attempt}/{_MAX_RETRIES}. Reintentando en {_RETRY_DELAY}s..."
        )
        time.sleep(_RETRY_DELAY)
    raise RuntimeError(f"EUR-Lex no devolvio contenido tras {_MAX_RETRIES} intentos: {url}")


def download() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(_HEADERS)

    for filename, url in SOURCES.items():
        dest = OUT_DIR / filename
        # Omitir solo si el fichero existe Y tiene contenido real
        if dest.exists() and dest.stat().st_size >= _MIN_BYTES:
            logger.info(f"Ya existe: {dest} ({dest.stat().st_size:,} bytes), omitiendo")
            continue
        logger.info(f"Descargando {url}")
        content = _fetch_with_retry(session, url)
        dest.write_bytes(content)
        logger.success(f"Guardado: {dest} ({len(content):,} bytes)")


if __name__ == "__main__":
    download()
