"""Parsea los HTML descargados de EUR-Lex y extrae articulos individuales.

Salida: data/interim/articles_ai_act.jsonl y data/interim/articles_rgpd.jsonl.
Cada linea es un JSON con: {norm, article_number, title, text, char_count}.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from loguru import logger

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/interim")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_articles(html_path: Path, norm: str) -> list[dict]:
    """Extrae articulos del HTML de EUR-Lex.

    EUR-Lex usa:
      <p class="ti-art">  → numero de articulo  (p.ej. "Artículo 6")
      <p class="sti-art"> → titulo del articulo (p.ej. "Condiciones de licitud")
      <p class="normal">  → cuerpo del articulo
    """
    # Dejar que BeautifulSoup detecte la codificacion desde el <meta> del HTML
    raw_bytes = html_path.read_bytes()
    soup = BeautifulSoup(raw_bytes, "html.parser")

    _ART_RE = re.compile(r"^Art[ií]?culo\s+(\d+[a-zA-Z]?)\s*$", re.IGNORECASE)

    articles: list[dict] = []
    current: dict | None = None

    for elem in soup.find_all(["p", "div"]):
        cls = elem.get("class", [])
        text = clean_text(elem.get_text())

        # Titulo de articulo: clase ti-art o texto que coincide con el patron
        is_art_header = "ti-art" in cls or bool(_ART_RE.match(text))
        if is_art_header:
            m = _ART_RE.match(text)
            if m:
                if current is not None:
                    articles.append(current)
                current = {
                    "norm": norm,
                    "article_number": m.group(1),
                    "title": "",
                    "text": "",
                }
                continue

        if current is None:
            continue

        # Titulo explícito del articulo via clase sti-art
        if "sti-art" in cls and not current["title"] and text:
            current["title"] = text
            continue

        # Heuristica de respaldo: primer bloque corto sin clase especial
        if not current["title"] and text and len(text) < 200 and "ti-art" not in cls:
            current["title"] = text
            continue

        # Acumular cuerpo (excluir cabeceras de articulo)
        if text and "ti-art" not in cls and "sti-art" not in cls:
            current["text"] += " " + text

    if current is not None:
        articles.append(current)

    for a in articles:
        a["text"] = clean_text(a["text"])
        a["char_count"] = len(a["text"])

    return [a for a in articles if a["char_count"] > 50]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = [
        (RAW_DIR / "ai_act.html", "AI_ACT", OUT_DIR / "articles_ai_act.jsonl"),
        (RAW_DIR / "rgpd.html", "RGPD", OUT_DIR / "articles_rgpd.jsonl"),
    ]

    for src, norm, dest in sources:
        if not src.exists() or src.stat().st_size == 0:
            logger.error(f"No existe o esta vacio: {src}. Corre antes scripts/download_norms.py")
            continue

        logger.info(f"Parseando {src} ({src.stat().st_size:,} bytes)")
        articles = extract_articles(src, norm)

        with dest.open("w", encoding="utf-8") as f:
            for a in articles:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")

        logger.success(f"{len(articles)} articulos guardados en {dest}")
        logger.info(f"Total chars: {sum(a['char_count'] for a in articles):,}")


if __name__ == "__main__":
    main()
