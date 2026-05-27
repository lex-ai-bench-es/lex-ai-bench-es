"""Mapeo de articulos a bloques tematicos.

Cada bloque agrupa articulos que comparten tema. Los rangos vienen del
articulado oficial. Editar aqui si cambia el plan de cobertura.
"""

from __future__ import annotations

# Cada entrada: (nombre_bloque, lista_de_articulos_como_strings)
# Los strings deben coincidir con el campo "article_number" de los JSONL
# parseados en data/interim/.

AI_ACT_BLOCKS = {
    "Disposiciones generales": ["1", "2", "3", "4"],
    "Practicas prohibidas": ["5"],
    "Sistemas de alto riesgo (clasificacion)": ["6", "7"],
    "Requisitos sistemas alto riesgo": ["8", "9", "10", "11", "12", "13", "14", "15"],
    "Obligaciones proveedores y deployers": [
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
    ],
    "Autoridades notificantes y organismos": [
        "28",
        "29",
        "30",
        "31",
        "32",
        "33",
        "34",
        "35",
        "36",
        "37",
        "38",
        "39",
    ],
    "Modelos GPAI": ["51", "52", "53", "54", "55", "56"],
    "Sandboxes regulatorios": ["57", "58", "59", "60", "61", "62", "63"],
    "Gobernanza": ["64", "65", "66", "67", "68", "69"],
    "Sanciones": ["99"],
    "Entrada en vigor": ["113"],
}

RGPD_BLOCKS = {
    "Disposiciones generales y ambito": ["1", "2", "3"],
    "Principios": ["5"],
    "Bases juridicas": ["6", "7", "8", "9", "10"],
    "Derechos del interesado": [
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
    ],
    "Obligaciones responsable y encargado": [
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
    ],
    "Seguridad y brechas": ["32", "33", "34"],
    "DPIA y DPO": ["35", "36", "37", "38", "39"],
    "Transferencias internacionales": [
        "44",
        "45",
        "46",
        "47",
        "48",
        "49",
        "50",
    ],
    "Autoridades de control": ["51", "52", "53", "54", "55", "56", "57", "58", "59"],
    "Recursos y sanciones": ["77", "78", "79", "80", "81", "82", "83", "84"],
}
