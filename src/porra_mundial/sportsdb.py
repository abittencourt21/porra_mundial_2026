from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import urlopen


BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
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

