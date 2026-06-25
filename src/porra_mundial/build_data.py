from __future__ import annotations

import argparse
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import os
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.request import urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import Match
from .scoring import build_datos_json
from .sheets import load_public_tsv_inputs, load_sheet_inputs
from .sportsdb import fetch_world_cup_events_for_date, parse_events, search_events


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PREVIOUS_DATOS_URL = "https://abittencourt21.github.io/porra_mundial_2026/datos.json"
try:
    LOCAL_TIMEZONE = ZoneInfo("Europe/Madrid")
except ZoneInfoNotFoundError:
    LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo or timezone.utc
RANKING_CHECKPOINTS = (
    ("pre", "Pre"),
    ("J1", "J1"),
    ("J2", "J2"),
    ("J3", "J3"),
    ("R32", "R32"),
    ("R16", "R16"),
    ("QF", "QF"),
    ("SF", "SF"),
    ("F", "Final"),
)
RANKING_CHECKPOINT_IDS = {checkpoint for checkpoint, _label in RANKING_CHECKPOINTS}
KO_CHECKPOINT_ORDER = {"R32": 4, "R16": 5, "QF": 6, "SF": 7, "F": 8}

_RAW_TEAM_ALIASES = {
    "argentina": "argentina",
    "algeria": "argelia",
    "argelia": "argelia",
    "australia": "australia",
    "austria": "austria",
    "belgica": "belgica",
    "bélgica": "belgica",
    "belgium": "belgica",
    "bosnia and herzegovina": "bosnia y herzegovina",
    "bosnia herzegovina": "bosnia y herzegovina",
    "bosnia-herzegovina": "bosnia y herzegovina",
    "bosnia & herzegovina": "bosnia y herzegovina",
    "bosnia y herzegovina": "bosnia y herzegovina",
    "brazil": "brasil",
    "brasil": "brasil",
    "canada": "canada",
    "canadá": "canada",
    "cape verde": "cabo verde",
    "cabo verde": "cabo verde",
    "catar": "catar",
    "colombia": "colombia",
    "corea del sur": "corea del sur",
    "cote d ivoire": "costa de marfil",
    "côte d'ivoire": "costa de marfil",
    "côte d’ivoire": "costa de marfil",
    "cote divoire": "costa de marfil",
    "côte divoire": "costa de marfil",
    "costa de marfil": "costa de marfil",
    "croatia": "croacia",
    "croacia": "croacia",
    "curacao": "curazao",
    "curaçao": "curazao",
    "curazao": "curazao",
    "czech rep": "chequia",
    "czech republic": "chequia",
    "czechia": "chequia",
    "chequia": "chequia",
    "democratic republic of congo": "rd congo",
    "congo dr": "rd congo",
    "dr congo": "rd congo",
    "d r congo": "rd congo",
    "rd congo": "rd congo",
    "ecuador": "ecuador",
    "egypt": "egipto",
    "egipto": "egipto",
    "england": "inglaterra",
    "inglaterra": "inglaterra",
    "france": "francia",
    "francia": "francia",
    "germany": "alemania",
    "alemania": "alemania",
    "ghana": "ghana",
    "haiti": "haiti",
    "iran": "iran",
    "iraq": "irak",
    "irak": "irak",
    "ivory coast": "costa de marfil",
    "japan": "japon",
    "japon": "japon",
    "jordan": "jordania",
    "jordania": "jordania",
    "mexico": "mexico",
    "méxico": "mexico",
    "morocco": "marruecos",
    "marruecos": "marruecos",
    "netherlands": "paises bajos",
    "países bajos": "paises bajos",
    "holland": "paises bajos",
    "paises bajos": "paises bajos",
    "new zealand": "nueva zelanda",
    "nueva zelanda": "nueva zelanda",
    "norway": "noruega",
    "noruega": "noruega",
    "panama": "panama",
    "panamá": "panama",
    "paraguay": "paraguay",
    "portugal": "portugal",
    "qatar": "catar",
    "saudi arabia": "arabia saudi",
    "arabia saudi": "arabia saudi",
    "arabia saudí": "arabia saudi",
    "scotland": "escocia",
    "escocia": "escocia",
    "senegal": "senegal",
    "south africa": "sudafrica",
    "sudafrica": "sudafrica",
    "sudáfrica": "sudafrica",
    "korea republic": "corea del sur",
    "republic of korea": "corea del sur",
    "korea south": "corea del sur",
    "south korea": "corea del sur",
    "spain": "espana",
    "españa": "espana",
    "espana": "espana",
    "suecia": "suecia",
    "sweden": "suecia",
    "switzerland": "suiza",
    "suiza": "suiza",
    "tunisia": "tunez",
    "túnez": "tunez",
    "tunez": "tunez",
    "turkey": "turquia",
    "türkiye": "turquia",
    "turkiye": "turquia",
    "turquía": "turquia",
    "turquia": "turquia",
    "united states": "estados unidos",
    "united states of america": "estados unidos",
    "us": "estados unidos",
    "usa": "estados unidos",
    "estados unidos": "estados unidos",
    "uruguay": "uruguay",
    "uzbekistan": "uzbekistan",
    "uzbekistán": "uzbekistan",
}


def _normalize_team_text(value: Any) -> str:
    text = str(value or "").casefold().strip()
    normalized = unicodedata.normalize("NFKD", text)
    cleaned = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", cleaned).strip()


TEAM_ALIASES = {
    _normalize_team_text(alias): _normalize_team_text(canonical)
    for alias, canonical in _RAW_TEAM_ALIASES.items()
}
SPORTSDB_SEARCH_NAMES = {
    "arabia saudi": "Saudi Arabia",
    "belgica": "Belgium",
    "bosnia y herzegovina": "Bosnia-Herzegovina",
    "brasil": "Brazil",
    "cabo verde": "Cape Verde",
    "canada": "Canada",
    "catar": "Qatar",
    "chequia": "Czech Republic",
    "colombia": "Colombia",
    "corea del sur": "South Korea",
    "costa de marfil": "Cote d'Ivoire",
    "croacia": "Croatia",
    "curazao": "Curacao",
    "egipto": "Egypt",
    "espana": "Spain",
    "estados unidos": "USA",
    "francia": "France",
    "ghana": "Ghana",
    "inglaterra": "England",
    "irak": "Iraq",
    "iran": "Iran",
    "japon": "Japan",
    "jordania": "Jordan",
    "marruecos": "Morocco",
    "mexico": "Mexico",
    "nueva zelanda": "New Zealand",
    "paises bajos": "Netherlands",
    "panama": "Panama",
    "rd congo": "DR Congo",
    "sudafrica": "South Africa",
    "tunez": "Tunisia",
    "turquia": "Turkiye",
    "uzbekistan": "Uzbekistan",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera datos.json para la web estatica.")
    parser.add_argument("--out", default="public/datos.json", help="Ruta de salida del JSON.")
    args = parser.parse_args()

    inputs = _load_inputs()
    previous_payload = _load_previous_payload()
    build_date = _build_date()
    matches, live_source_used, sportsdb_alerts = _load_matches(inputs, previous_payload, build_date)
    meta = dict(inputs.get("meta", {}))
    meta["ultima_actualizacion"] = datetime.now(timezone.utc).isoformat()
    meta["fecha_actualizacion_local"] = build_date
    if live_source_used:
        meta["fuente"] = "TheSportsDB liga 4429"

    overrides = inputs.get("overrides", [])
    matches, meta, goleadores = _apply_overrides(
        matches,
        overrides,
        meta,
        list(inputs.get("goleadores", [])),
    )
    payload = build_datos_json(
        participants=inputs["participantes"],
        matches=matches,
        team_bombos=inputs["bombos"],
        meta=meta,
        goleadores=goleadores,
    )
    payload["meta"].update(
        {
            "fecha_actualizacion_local": build_date,
        }
    )
    _enrich_ranking(payload, previous_payload, build_date)

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generado {out_path}")
    for alert in sportsdb_alerts:
        print(f"::warning::{alert}")


def _load_seed(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_inputs() -> dict:
    seed = _load_seed(ROOT / "data" / "seed.json")
    public_tsv_url = os.getenv("GOOGLE_SHEET_TSV_URL")
    if public_tsv_url:
        return load_public_tsv_inputs(
            tsv_url=public_tsv_url,
            seed=seed,
            overrides_tsv_url=os.getenv("GOOGLE_OVERRIDES_TSV_URL"),
        )

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sheet_id and service_account_json:
        return load_sheet_inputs(
            spreadsheet_id=sheet_id,
            service_account_json=service_account_json,
            seed=seed,
            quinielas_range=os.getenv("GOOGLE_QUINIELAS_RANGE", "quinielas!A:Z"),
            overrides_range=os.getenv("GOOGLE_OVERRIDES_RANGE", "overrides!A:Z"),
        )
    return seed


def _load_previous_payload() -> dict[str, Any] | None:
    previous_url = os.getenv("PREVIOUS_DATOS_URL", DEFAULT_PREVIOUS_DATOS_URL).strip()
    if not previous_url:
        return None
    try:
        with urlopen(previous_url, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def _build_date() -> str:
    explicit = os.getenv("BUILD_DATE", "").strip()
    if explicit:
        return _normalize_date(explicit)
    return datetime.now(LOCAL_TIMEZONE).date().isoformat()


def _load_matches(
    inputs: dict[str, Any],
    previous_payload: dict[str, Any] | None = None,
    build_date: str | None = None,
) -> tuple[list[Match], bool, list[str]]:
    base_matches = [Match.from_dict(match) for match in inputs.get("partidos", [])]
    matches = _merge_previous_scores(base_matches, previous_payload)
    target_date = _normalize_date(build_date or _build_date())
    fetch_dates = _sportsdb_fetch_dates(target_date)
    expected_today = [match for match in matches if _normalize_date(match.fecha) in fetch_dates]
    alerts: list[str] = []

    if not expected_today:
        return matches, False, alerts
    if all(_has_result(match) for match in expected_today):
        return matches, False, alerts

    try:
        parsed = []
        for fetch_date in fetch_dates:
            payload = fetch_world_cup_events_for_date(fetch_date)
            parsed.extend(parse_events(payload))
        parsed.extend(_search_missing_events(matches, parsed, expected_today))
        if parsed:
            patched, merge_alerts = _merge_live_scores(matches, parsed, expected_today=expected_today)
            return patched, True, merge_alerts
        alerts.append(
            f"SportsDB no devolvió eventos para {', '.join(fetch_dates)}. Esperados: {len(expected_today)}."
        )
    except Exception as exc:
        alerts.append(f"No se pudo consultar SportsDB para {', '.join(fetch_dates)}: {exc}")
    return matches, False, alerts


def _sportsdb_fetch_dates(target_date: str) -> list[str]:
    date = datetime.fromisoformat(_normalize_date(target_date)).date()
    return [
        (date - timedelta(days=1)).isoformat(),
        date.isoformat(),
    ]


def _search_missing_events(
    seed_matches: list[Match],
    live_matches: list[Match],
    expected_today: list[Match],
) -> list[Match]:
    missing = _missing_expected_matches(seed_matches, live_matches, expected_today)
    fallback_matches: list[Match] = []
    for match in missing:
        for event_name in _sportsdb_search_event_names(match):
            try:
                payload = search_events(event_name)
            except Exception:
                continue
            parsed = parse_events(payload)
            matched = [
                live_match
                for live_match in parsed
                if _find_seed_match(seed_matches, live_match) is not None
            ]
            fallback_matches.extend(matched)
            if matched:
                break
    return fallback_matches


def _merge_previous_scores(
    seed_matches: list[Match],
    previous_payload: dict[str, Any] | None,
) -> list[Match]:
    if not previous_payload:
        return seed_matches

    previous_matches = [
        Match.from_dict(match)
        for match in previous_payload.get("partidos", [])
    ]
    patched = list(seed_matches)
    for previous_match in previous_matches:
        if not _has_result(previous_match):
            continue
        match_index = _find_seed_match(patched, previous_match)
        if match_index is None:
            continue
        patched[match_index] = _patch_live_score(patched[match_index], previous_match)
    return patched


def _merge_live_scores(
    seed_matches: list[Match],
    live_matches: list[Match],
    *,
    expected_today: list[Match] | None = None,
) -> tuple[list[Match], list[str]]:
    patched = list(seed_matches)
    alerts: list[str] = []

    for live_match in live_matches:
        match_index = _find_seed_match(patched, live_match)
        if match_index is None:
            alerts.append(
                f"Evento SportsDB sin emparejar: {live_match.home_team} vs {live_match.away_team} ({live_match.fecha})."
            )
            continue
        patched[match_index] = _patch_live_score(patched[match_index], live_match)

    if expected_today:
        for match in _missing_expected_matches(seed_matches, live_matches, expected_today):
            alerts.append(
                f"SportsDB no devolvió partido esperado: {match.home_team} vs {match.away_team} ({match.fecha})."
            )

    return patched, alerts


def _find_seed_match(seed_matches: list[Match], live_match: Match) -> int | None:
    live_pair = _team_pair_key(live_match)
    if not live_pair:
        return None

    candidates: list[int] = []
    for index, seed_match in enumerate(seed_matches):
        if _team_pair_key(seed_match) != live_pair:
            continue
        if _normalize_date(seed_match.fecha) != _normalize_date(live_match.fecha):
            continue
        candidates.append(index)

    return candidates[0] if len(candidates) == 1 else None


def _missing_expected_matches(
    seed_matches: list[Match],
    live_matches: list[Match],
    expected_today: list[Match],
) -> list[Match]:
    found_indexes = {
        index
        for live_match in live_matches
        if (index := _find_seed_match(seed_matches, live_match)) is not None
    }
    return [
        match
        for index, match in enumerate(seed_matches)
        if any(match.matchid == expected.matchid for expected in expected_today)
        and index not in found_indexes
        and not _has_result(match)
    ]


def _sportsdb_search_event_names(match: Match) -> list[str]:
    home = _sportsdb_search_team_name(match.home_team)
    away = _sportsdb_search_team_name(match.away_team)
    if not home or not away:
        return []
    home_slug = _sportsdb_search_slug(home)
    away_slug = _sportsdb_search_slug(away)
    return [
        f"{home_slug}_vs_{away_slug}",
        f"{away_slug}_vs_{home_slug}",
    ]


def _sportsdb_search_team_name(value: Any) -> str:
    team = _team_key(value)
    return SPORTSDB_SEARCH_NAMES.get(team, str(value or "").strip())


def _sportsdb_search_slug(value: str) -> str:
    return re.sub(r"\s+", "_", value.strip())


def _patch_live_score(seed_match: Match, live_match: Match) -> Match:
    same_orientation = _team_key(seed_match.home_team) == _team_key(live_match.home_team)
    if same_orientation:
        home_score = live_match.home_score
        away_score = live_match.away_score
        home_score_90 = live_match.home_score_90
        away_score_90 = live_match.away_score_90
    else:
        home_score = live_match.away_score
        away_score = live_match.home_score
        home_score_90 = live_match.away_score_90
        away_score_90 = live_match.home_score_90

    return replace(
        seed_match,
        home_score=home_score,
        away_score=away_score,
        home_score_90=home_score_90,
        away_score_90=away_score_90,
        status=live_match.status or seed_match.status,
    )


def _has_result(match: Match) -> bool:
    return match.home_score is not None and match.away_score is not None


def _enrich_ranking(
    payload: dict[str, Any],
    previous_payload: dict[str, Any] | None,
    build_date: str,
) -> None:
    participants = payload.get("participantes", [])
    checkpoint_id = _ranking_checkpoint_id(payload, build_date)
    checkpoint_label = _ranking_checkpoint_label(payload, build_date)
    previous_history = []
    if previous_payload:
        previous_history = _normalize_ranking_history(
            previous_payload.get("meta", {}).get("ranking_history", [])
        )
    previous_positions = _previous_positions(previous_payload, checkpoint_id, previous_history)

    for index, participant in enumerate(participants, start=1):
        alias = str(participant.get("alias", ""))
        previous_rank = previous_positions.get(alias)
        participant["rank_actual"] = index
        participant["rank_anterior"] = previous_rank
        participant["rank_delta"] = None if previous_rank is None else previous_rank - index
        participant["rank_status"] = "nuevo" if previous_rank is None else (
            "sube" if previous_rank > index else "baja" if previous_rank < index else "igual"
        )

    current_rows = [
        {
            "checkpoint": checkpoint_id,
            "label": checkpoint_label,
            "fecha": build_date,
            "alias": participant.get("alias", ""),
            "posicion": participant.get("rank_actual"),
            "puntos": participant.get("puntos_total", 0),
        }
        for participant in participants
    ]
    payload["meta"]["ranking_history"] = [
        row for row in previous_history if row.get("checkpoint") != checkpoint_id
    ] + current_rows
    payload["meta"]["ranking_checkpoints"] = [
        {"checkpoint": checkpoint, "label": label}
        for checkpoint, label in RANKING_CHECKPOINTS
    ]


def _previous_positions(
    previous_payload: dict[str, Any] | None,
    current_checkpoint: str,
    previous_history: list[dict[str, Any]],
) -> dict[str, int]:
    positions: dict[str, int] = {}
    if previous_payload:
        for index, participant in enumerate(previous_payload.get("participantes", []), start=1):
            positions[str(participant.get("alias", ""))] = int(participant.get("rank_actual") or index)
    positions.update(_previous_checkpoint_positions(previous_history, current_checkpoint))
    return positions


def _previous_checkpoint_positions(
    previous_history: list[dict[str, Any]],
    current_checkpoint: str,
) -> dict[str, int]:
    latest_checkpoint = ""
    for row in previous_history:
        checkpoint = str(row.get("checkpoint") or "")
        if checkpoint and checkpoint != current_checkpoint:
            latest_checkpoint = checkpoint
    if not latest_checkpoint:
        return {}
    return {
        str(row.get("alias", "")): int(row.get("posicion") or 0)
        for row in previous_history
        if row.get("checkpoint") == latest_checkpoint and row.get("alias") and row.get("posicion")
    }


def _ranking_checkpoint_id(payload: dict[str, Any], build_date: str) -> str:
    completed = [
        Match.from_dict(match)
        for match in payload.get("partidos", [])
        if _has_result(Match.from_dict(match))
    ]
    if not completed:
        return "pre"

    ko_rounds = [
        match.ronda
        for match in completed
        if match.ronda in KO_CHECKPOINT_ORDER
    ]
    if ko_rounds:
        return max(ko_rounds, key=lambda round_name: KO_CHECKPOINT_ORDER[round_name])

    group_rounds = [
        int(match.roundnumber)
        for match in completed
        if match.ronda == "grupos" and match.roundnumber is not None
    ]
    if group_rounds:
        return f"J{min(max(group_rounds), 3)}"
    return "pre"


def _ranking_checkpoint_label(payload: dict[str, Any], build_date: str) -> str:
    checkpoint = _ranking_checkpoint_id(payload, build_date)
    labels = dict(RANKING_CHECKPOINTS)
    return labels.get(checkpoint, checkpoint)


def _normalize_ranking_history(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        checkpoint = _normalize_ranking_checkpoint(row.get("checkpoint"))
        alias = str(row.get("alias", ""))
        if not checkpoint or not alias:
            continue
        patched = dict(row)
        patched["checkpoint"] = checkpoint
        patched["label"] = dict(RANKING_CHECKPOINTS).get(checkpoint, str(row.get("label") or checkpoint))
        normalized[(checkpoint, alias)] = patched
    return list(normalized.values())


def _normalize_ranking_checkpoint(value: Any) -> str:
    checkpoint = str(value or "").strip()
    if checkpoint in RANKING_CHECKPOINT_IDS:
        return checkpoint
    if "-J" in checkpoint:
        return checkpoint.rsplit("-", 1)[-1]
    return checkpoint if checkpoint in RANKING_CHECKPOINT_IDS else ""


def _apply_overrides(
    matches: list[Match],
    overrides: list[dict[str, Any]],
    meta: dict[str, Any],
    goleadores: list[dict[str, Any]],
) -> tuple[list[Match], dict[str, Any], list[dict[str, Any]]]:
    patched_matches = list(matches)
    patched_meta = dict(meta)
    patched_goleadores = list(goleadores)

    for override in overrides:
        kind = _override_kind(override)
        if kind == "meta":
            _apply_meta_override(patched_meta, override)
        elif kind == "goleador":
            _apply_goleador_override(patched_goleadores, override)
        else:
            _apply_match_override(patched_matches, override)

    return patched_matches, patched_meta, patched_goleadores


def _override_kind(row: dict[str, Any]) -> str:
    explicit = str(row.get("tipo") or row.get("type") or row.get("kind") or "").casefold()
    if explicit in {"meta", "goleador", "match"}:
        return explicit
    if any(key in row for key in ("jugador", "goles")):
        return "goleador"
    if any(
        key in row
        for key in (
            "home_score",
            "away_score",
            "home_score_90",
            "away_score_90",
            "pasa",
            "status",
            "matchid",
            "idevent",
            "home_team",
            "away_team",
            "roundnumber",
            "group",
        )
    ):
        return "match"
    return "meta"


def _apply_meta_override(meta: dict[str, Any], row: dict[str, Any]) -> None:
    for key in (
        "fuente",
        "ultima_actualizacion",
        "estado_torneo",
        "campeon",
        "subcampeon",
        "pichichi_nombre",
        "pichichi_goles",
    ):
        if key in row and row[key] != "":
            meta[key] = _coerce_value(key, row[key])


def _apply_goleador_override(goleadores: list[dict[str, Any]], row: dict[str, Any]) -> None:
    jugador = str(row.get("jugador") or row.get("player") or row.get("nombre") or "").strip()
    if not jugador:
        return
    goles = _to_int(row.get("goles"))
    entry = {"jugador": jugador, "goles": goles if goles is not None else 0}
    goleadores.append(entry)


def _apply_match_override(matches: list[Match], row: dict[str, Any]) -> None:
    selected = _select_matches(matches, row)
    if not selected:
        return
    for index, match in selected:
        matches[index] = _patch_match(match, row)


def _select_matches(matches: list[Match], row: dict[str, Any]) -> list[tuple[int, Match]]:
    match_id = _to_int(row.get("matchid") or row.get("idevent") or row.get("id_event"))
    if match_id is not None:
        return [(index, match) for index, match in enumerate(matches) if match.matchid == match_id]

    home = str(row.get("home_team") or row.get("equipo_local") or row.get("local") or "").strip()
    away = str(row.get("away_team") or row.get("equipo_visitante") or row.get("visitante") or "").strip()
    date = str(row.get("fecha") or row.get("dateevent") or row.get("date") or "").strip()
    roundnumber = _to_int(row.get("roundnumber") or row.get("jornada"))

    candidates: list[tuple[int, Match]] = []
    for index, match in enumerate(matches):
        if home and away:
            pair = {_team_key(match.home_team), _team_key(match.away_team)}
            desired = {_team_key(home), _team_key(away)}
            if pair != desired:
                continue
        elif home or away:
            target = _team_key(home or away)
            if target not in {_team_key(match.home_team), _team_key(match.away_team)}:
                continue
        if date and _normalize_date(match.fecha) != _normalize_date(date):
            continue
        if roundnumber is not None and match.roundnumber != roundnumber:
            continue
        candidates.append((index, match))
    return candidates


def _patch_match(match: Match, row: dict[str, Any]) -> Match:
    home_score = _to_int(row.get("home_score"))
    away_score = _to_int(row.get("away_score"))
    home_score_90 = _to_int(row.get("home_score_90"))
    away_score_90 = _to_int(row.get("away_score_90"))
    if home_score_90 is None and home_score is not None:
        home_score_90 = home_score
    if away_score_90 is None and away_score is not None:
        away_score_90 = away_score

    updates: dict[str, Any] = {}
    for key, value in (
        ("group", row.get("group")),
        ("roundnumber", _to_int(row.get("roundnumber"))),
        ("ronda", row.get("ronda")),
        ("fecha", row.get("fecha")),
        ("home_team", row.get("home_team")),
        ("away_team", row.get("away_team")),
        ("home_score", home_score),
        ("away_score", away_score),
        ("home_score_90", home_score_90),
        ("away_score_90", away_score_90),
        ("pasa", row.get("pasa")),
        ("status", row.get("status")),
    ):
        if value not in (None, ""):
            updates[key] = value
    return replace(match, **updates)


def _coerce_value(key: str, value: Any) -> Any:
    if key == "pichichi_goles":
        return _to_int(value) or 0
    return value


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _team_key(value: Any) -> str:
    cleaned = _normalize_team_text(value)
    return TEAM_ALIASES.get(cleaned, cleaned)


def _team_pair_key(match: Match) -> frozenset[str]:
    home = _team_key(match.home_team)
    away = _team_key(match.away_team)
    return frozenset(team for team in (home, away) if team)


def _normalize_date(value: str) -> str:
    text = str(value or "").replace(".", "-").replace("/", "-").strip()
    parts = text.split("-")
    if len(parts) != 3:
        return text
    if len(parts[0]) == 4:
        year, month, day = parts
    else:
        day, month, year = parts
    return f"{year.zfill(4)}-{month.zfill(2)}-{day.zfill(2)}"

if __name__ == "__main__":
    main()
