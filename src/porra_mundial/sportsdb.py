from __future__ import annotations

from collections import Counter
import json
import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from .models import Match


API_KEY = os.getenv("SPORTSDB_API_KEY", "123")
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"
WORLD_CUP_LEAGUE_ID = "4429"


def fetch_world_cup_events(season: str = "2026") -> dict:
    """Descarga eventos de TheSportsDB.

    Queda aislado para poder ajustar el parser cuando confirmemos que campos
    reales devuelve la temporada 2026 para resultado a 90', clasificado y goles.
    """
    query = urlencode({"id": WORLD_CUP_LEAGUE_ID, "s": season})
    url = f"{BASE_URL}/eventsseason.php?{query}"
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_world_cup_events_for_date(date: str) -> dict:
    """Descarga eventos de la Copa del Mundo para un dia concreto."""
    query = urlencode({"d": date, "l": WORLD_CUP_LEAGUE_ID})
    url = f"{BASE_URL}/eventsday.php?{query}"
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_world_cup_events_for_round(round_number: int, season: str = "2026") -> dict:
    """Descarga todos los eventos de una ronda de la Copa del Mundo."""
    query = urlencode({"id": WORLD_CUP_LEAGUE_ID, "r": round_number, "s": season})
    url = f"{BASE_URL}/eventsround.php?{query}"
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def search_events(event_name: str, date: str | None = None) -> dict:
    """Busca eventos por titulo, opcionalmente acotados por fecha."""
    params = {"e": event_name}
    if date:
        params["d"] = date
    query = urlencode(params)
    url = f"{BASE_URL}/searchevents.php?{query}"
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_events(payload: dict[str, Any]) -> list[Match]:
    return [parse_event(event) for event in payload.get("events") or payload.get("event") or []]


def parse_event(event: dict[str, Any]) -> Match:
    """Convierte un evento de TheSportsDB al contrato interno de partidos.

    TheSportsDB no expone ahora el matchid FIFA 1-104. Hasta tener un mapa
    oficial, usamos `idEvent` como identificador tecnico estable.
    """
    ronda = _infer_ronda(event)
    home_team = event.get("strHomeTeam") or ""
    away_team = event.get("strAwayTeam") or ""
    home_score = _parse_int(event.get("intHomeScore"))
    away_score = _parse_int(event.get("intAwayScore"))
    home_score_extra = _parse_int(event.get("intHomeScoreExtra"))
    away_score_extra = _parse_int(event.get("intAwayScoreExtra"))
    return Match(
        matchid=int(event["idEvent"]),
        group=event.get("strGroup"),
        roundnumber=_parse_int(event.get("intRound")),
        ronda=ronda,
        fecha=_format_date(event.get("dateEventLocal") or event.get("dateEvent")),
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score,
        home_score_90=home_score,
        away_score_90=away_score,
        pasa=_infer_winner(
            ronda,
            home_team,
            away_team,
            home_score,
            away_score,
            event.get("strStatus"),
            home_score_extra,
            away_score_extra,
        ),
        status=event.get("strStatus") or "NS",
    )


def summarize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    events = payload.get("events") or []
    keys = sorted({key for event in events for key in event})
    statuses = Counter(str(event.get("strStatus")) for event in events)
    rounds = Counter(str(event.get("intRound")) for event in events)
    return {
        "event_count": len(events),
        "keys": keys,
        "statuses": dict(sorted(statuses.items())),
        "rounds": dict(sorted(rounds.items())),
        "sample": [
            {
                "idEvent": event.get("idEvent"),
                "dateEvent": event.get("dateEvent"),
                "intRound": event.get("intRound"),
                "strEvent": event.get("strEvent"),
                "strStatus": event.get("strStatus"),
                "intHomeScore": event.get("intHomeScore"),
                "intAwayScore": event.get("intAwayScore"),
            }
            for event in events[:10]
        ],
    }


def _parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _format_date(value: str | None) -> str:
    if not value:
        return ""
    year, month, day = value.split("-")
    return f"{day}.{month}.{year}"


def _infer_ronda(event: dict[str, Any]) -> str:
    if event.get("strGroup"):
        return "grupos"
    raw_round = " ".join(
        str(event.get(key) or "")
        for key in ("strEvent", "strRound", "strStage", "strDescriptionEN")
    ).casefold()
    if "round of 32" in raw_round or "r32" in raw_round:
        return "R32"
    if "round of 16" in raw_round or "r16" in raw_round:
        return "R16"
    if "quarter" in raw_round:
        return "QF"
    if "semi" in raw_round:
        return "SF"
    if "third" in raw_round:
        return "3RD"
    if "final" in raw_round:
        return "F"
    round_number = _parse_int(event.get("intRound"))
    return {
        32: "R32",
        16: "R16",
        125: "QF",
        150: "SF",
        160: "3RD",
        200: "F",
    }.get(
        round_number,
        "grupos",
    )


def _infer_winner(
    ronda: str,
    home_team: str,
    away_team: str,
    home_score: int | None,
    away_score: int | None,
    status: Any,
    home_score_extra: int | None = None,
    away_score_extra: int | None = None,
) -> str | None:
    if ronda == "grupos" or str(status or "").upper() not in {"FT", "AET", "AOT", "AP", "PEN"}:
        return None
    if home_score is not None and away_score is not None and home_score != away_score:
        return home_team if home_score > away_score else away_team
    if home_score_extra is None or away_score_extra is None or home_score_extra == away_score_extra:
        return None
    return home_team if home_score_extra > away_score_extra else away_team