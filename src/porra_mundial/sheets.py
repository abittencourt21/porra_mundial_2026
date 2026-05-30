from __future__ import annotations

import json
from typing import Any


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


FIELD_ALIASES = {
    "timestamp": {"timestamp", "marca temporal", "fecha"},
    "alias": {"alias", "apodo", "nombre visible"},
    "equipo_bombo_1": {"equipo del bombo 1", "bombo 1", "equipo bombo 1"},
    "equipo_bombo_2": {"equipo del bombo 2", "bombo 2", "equipo bombo 2"},
    "equipo_bombo_3": {"equipo del bombo 3", "bombo 3", "equipo bombo 3"},
    "equipo_bombo_4": {"equipo del bombo 4", "bombo 4", "equipo bombo 4"},
    "campeon": {"campeon", "campeón"},
    "subcampeon": {"subcampeon", "subcampeón"},
    "pichichi": {"pichichi", "bota de oro"},
    "pagado": {"pagado", "pago", "ha pagado"},
}


def load_sheet_inputs(
    *,
    spreadsheet_id: str,
    service_account_json: str,
    seed: dict[str, Any],
    quinielas_range: str,
    overrides_range: str,
) -> dict[str, Any]:
    """Lee Google Sheets y devuelve solo datos aptos para el motor publico."""
    values = _read_ranges(
        spreadsheet_id=spreadsheet_id,
        service_account_json=service_account_json,
        ranges=[quinielas_range, overrides_range],
    )
    quinielas_rows = _rows_to_dicts(values.get(quinielas_range, []))

    output = dict(seed)
    output["participantes"] = [
        _sanitize_participant(row)
        for row in quinielas_rows
        if _has_public_pick_data(row)
    ]
    return output


def _read_ranges(
    *,
    spreadsheet_id: str,
    service_account_json: str,
    ranges: list[str],
) -> dict[str, list[list[str]]]:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    info = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
    )
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    result = (
        service.spreadsheets()
        .values()
        .batchGet(spreadsheetId=spreadsheet_id, ranges=ranges)
        .execute()
    )
    value_ranges = result.get("valueRanges", [])
    return {
        requested_range: value_ranges[index].get("values", [])
        for index, requested_range in enumerate(ranges)
        if index < len(value_ranges)
    }


def _rows_to_dicts(values: list[list[str]]) -> list[dict[str, str]]:
    if not values:
        return []
    headers = [_normalize_header(value) for value in values[0]]
    rows = []
    for raw_row in values[1:]:
        padded = raw_row + [""] * (len(headers) - len(raw_row))
        row = {headers[index]: value.strip() for index, value in enumerate(padded[: len(headers)])}
        rows.append(row)
    return rows


def _sanitize_participant(row: dict[str, str]) -> dict[str, Any]:
    return {
        "timestamp": _get(row, "timestamp"),
        "alias": _get(row, "alias"),
        "equipos": [
            _get(row, "equipo_bombo_1"),
            _get(row, "equipo_bombo_2"),
            _get(row, "equipo_bombo_3"),
            _get(row, "equipo_bombo_4"),
        ],
        "campeon": _get(row, "campeon"),
        "subcampeon": _get(row, "subcampeon"),
        "pichichi": _get(row, "pichichi"),
        "pagado": _parse_bool(_get(row, "pagado")),
    }


def _has_public_pick_data(row: dict[str, str]) -> bool:
    return bool(_get(row, "alias") and _get(row, "equipo_bombo_1"))


def _get(row: dict[str, str], canonical: str) -> str:
    for alias in FIELD_ALIASES[canonical]:
        value = row.get(_normalize_header(alias), "")
        if value:
            return value
    return ""


def _parse_bool(value: str) -> bool:
    return _normalize_header(value) in {"si", "sí", "yes", "true", "1", "pagado", "ok"}


def _normalize_header(value: str) -> str:
    normalized = value.casefold().strip()
    replacements = str.maketrans({"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"})
    return " ".join(normalized.translate(replacements).split())
