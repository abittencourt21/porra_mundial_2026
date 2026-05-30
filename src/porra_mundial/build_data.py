from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .scoring import build_datos_json
from .sheets import load_sheet_inputs


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera datos.json para la web estatica.")
    parser.add_argument("--out", default="public/datos.json", help="Ruta de salida del JSON.")
    args = parser.parse_args()

    seed = _load_inputs()
    payload = build_datos_json(
        participants=seed["participantes"],
        matches=seed["partidos"],
        team_bombos=seed["bombos"],
        meta=seed["meta"],
        goleadores=seed.get("goleadores", []),
    )

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generado {out_path}")


def _load_seed(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_inputs() -> dict:
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sheet_id and service_account_json:
        return load_sheet_inputs(
            spreadsheet_id=sheet_id,
            service_account_json=service_account_json,
            seed=_load_seed(ROOT / "data" / "seed.json"),
            quinielas_range=os.getenv("GOOGLE_QUINIELAS_RANGE", "quinielas!A:Z"),
            overrides_range=os.getenv("GOOGLE_OVERRIDES_RANGE", "overrides!A:Z"),
        )
    return _load_seed(ROOT / "data" / "seed.json")


if __name__ == "__main__":
    main()
