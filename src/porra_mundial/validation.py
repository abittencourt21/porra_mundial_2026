from __future__ import annotations

from itertools import combinations
from typing import Any, Iterable

from .models import ParticipantPick


def find_combination_conflicts(
    participants: Iterable[ParticipantPick | dict[str, Any]],
    *,
    max_intersection: int = 2,
) -> list[dict[str, Any]]:
    """Detecta quinielas que comparten demasiados equipos.

    La regla de la porra permite como maximo 2 equipos iguales entre dos
    participantes. Si hay conflicto, la entrada con timestamp anterior gana.
    """
    parsed = [
        p if isinstance(p, ParticipantPick) else ParticipantPick.from_dict(p)
        for p in participants
    ]
    conflicts: list[dict[str, Any]] = []

    for first, second in combinations(parsed, 2):
        shared = sorted(set(first.equipos) & set(second.equipos))
        if len(shared) <= max_intersection:
            continue

        winner, loser = _order_by_timestamp(first, second)
        conflicts.append(
            {
                "winner": winner.alias,
                "loser": loser.alias,
                "shared_teams": shared,
                "intersection": len(shared),
                "reason": "interseccion >= 3",
            }
        )

    return conflicts


def _order_by_timestamp(
    first: ParticipantPick,
    second: ParticipantPick,
) -> tuple[ParticipantPick, ParticipantPick]:
    if not first.timestamp:
        return second, first
    if not second.timestamp:
        return first, second
    if first.timestamp <= second.timestamp:
        return first, second
    return second, first

