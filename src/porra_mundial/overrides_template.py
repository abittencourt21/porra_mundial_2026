from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HEADERS = [
    "type",
    "matchid",
    "group",
    "roundnumber",
    "ronda",
    "fecha",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "home_score_90",
    "away_score_90",
    "pasa",
    "status",
    "estado_torneo",
    "campeon",
    "subcampeon",
    "pichichi_nombre",
    "pichichi_goles",
    "jugador",
    "goles",
    "notas",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera plantilla CSV para la pestana overrides.")
    parser.add_argument("--seed", default="data/seed.json", help="Ruta del seed base.")
    parser.add_argument("--out", default="data/overrides_template.csv", help="Ruta de salida CSV.")
    args = parser.parse_args()

    seed = json.loads((ROOT / args.seed).read_text(encoding="utf-8"))
    rows = build_overrides_template_rows(seed)
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_overrides_template(out_path, rows)
    print(f"Generado {out_path} ({len(rows)} filas + cabecera)")


def build_overrides_template_rows(seed: dict[str, Any]) -> list[dict[str, Any]]:
    meta = seed.get("meta", {})
    rows: list[dict[str, Any]] = [
        {
            "type": "meta",
            "estado_torneo": meta.get("estado_torneo", "pre"),
            "campeon": meta.get("campeon", ""),
            "subcampeon": meta.get("subcampeon", ""),
            "pichichi_nombre": meta.get("pichichi_nombre", ""),
            "pichichi_goles": meta.get("pichichi_goles", ""),
            "notas": "Fila opcional de estado global. Borra valores que no quieras forzar.",
        },
        {
            "type": "goleador",
            "jugador": "",
            "goles": "",
            "notas": "Fila ejemplo opcional. Duplica para meter goleadores manuales.",
        },
    ]

    for match in seed.get("partidos", []):
        rows.append(
            {
                "type": "match",
                "matchid": match.get("matchid", ""),
                "group": match.get("group", ""),
                "roundnumber": match.get("roundnumber", ""),
                "ronda": match.get("ronda", ""),
                "fecha": match.get("fecha", ""),
                "home_team": match.get("home_team", ""),
                "away_team": match.get("away_team", ""),
                "home_score": "",
                "away_score": "",
                "home_score_90": "",
                "away_score_90": "",
                "pasa": "",
                "status": "",
                "notas": "Rellena solo si quieres corregir este partido manualmente.",
            }
        )
    return rows


def write_overrides_template(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
