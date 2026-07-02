from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from .models import GROUP_ROUND, KO_ROUNDS, Match, ParticipantPick, TeamScore, TournamentMeta

BONUS_POINTS = {
    "campeon": 10,
    "subcampeon": 5,
    "pichichi": 7,
    "campeon_surprise": 6,
}
DRAW_AFTER_90_STATUSES = {"AET", "AOT", "AP", "PEN"}


def normalize_name(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def result_points(goals_for: int | None, goals_against: int | None) -> int:
    if goals_for is None or goals_against is None:
        return 0
    if goals_for > goals_against:
        return 3
    if goals_for == goals_against:
        return 1
    return 0


def score_participant(
    pick: ParticipantPick | dict[str, Any],
    matches: Iterable[Match | dict[str, Any]],
    team_bombos: dict[str, int],
    meta: TournamentMeta | dict[str, Any],
) -> dict[str, Any]:
    participant = pick if isinstance(pick, ParticipantPick) else ParticipantPick.from_dict(pick)
    parsed_matches = [m if isinstance(m, Match) else Match.from_dict(m) for m in matches]
    tournament = _meta_from_any(meta)

    team_scores = {
        team: TeamScore(team=team, bombo=team_bombos[team])
        for team in participant.equipos
    }
    reached_rounds = {team: set() for team in participant.equipos}

    for match in parsed_matches:
        for team, score in team_scores.items():
            if team not in (match.home_team, match.away_team):
                continue
            if match.ronda == GROUP_ROUND:
                gf, gc = _goals_for_team(match, team, use_90=False)
                score.g_pts += result_points(gf, gc)
            elif match.ronda in KO_ROUNDS:
                gf, gc = _goals_for_team(match, team, use_90=True)
                pts_resultado = (
                    1
                    if str(match.status or "").upper() in DRAW_AFTER_90_STATUSES
                    else result_points(gf, gc)
                )
                reached_round = match.ronda not in reached_rounds[team]
                pts_pase = score.bombo if reached_round else 0
                score.ko_result_pts += pts_resultado
                score.ko_pass_pts += pts_pase
                if reached_round:
                    reached_rounds[team].add(match.ronda)
                    score.rondas_pasadas.append(match.ronda)
                score.ko_det.append(
                    {
                        "ronda": match.ronda,
                        "rival": match.away_team if match.home_team == team else match.home_team,
                        "gf": gf,
                        "gc": gc,
                        "pts_resultado": pts_resultado,
                        "pts_pase": pts_pase,
                        "paso": reached_round,
                    }
                )

    desglose = {
        "grupos": sum(score.g_pts for score in team_scores.values()),
        "playoffs_resultado": sum(score.ko_result_pts for score in team_scores.values()),
        "playoffs_pase": sum(score.ko_pass_pts for score in team_scores.values()),
        "bonus_final": _final_bonus(participant, tournament),
    }

    return {
        "alias": participant.alias,
        "equipos": list(participant.equipos),
        "campeon": participant.campeon,
        "subcampeon": participant.subcampeon,
        "pichichi": participant.pichichi,
        "pagado": participant.pagado,
        "puntos_total": sum(desglose.values()),
        "desglose": desglose,
        "bonus_det": BONUS_POINTS.copy(),
        "team_data": [team_scores[team].to_dict() for team in participant.equipos],
    }


def build_datos_json(
    participants: Iterable[ParticipantPick | dict[str, Any]],
    matches: Iterable[Match | dict[str, Any]],
    team_bombos: dict[str, int],
    meta: TournamentMeta | dict[str, Any] | None = None,
    goleadores: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    parsed_matches = [m if isinstance(m, Match) else Match.from_dict(m) for m in matches]
    tournament = _meta_from_any(meta) if meta else TournamentMeta(
        ultima_actualizacion=datetime.now(timezone.utc).isoformat()
    )
    scored = [
        score_participant(participant, parsed_matches, team_bombos, tournament)
        for participant in participants
    ]
    scored.sort(key=lambda item: (-item["puntos_total"], item["alias"].casefold()))

    return {
        "meta": tournament.to_dict(),
        "participantes": scored,
        "partidos": [match.to_dict() for match in parsed_matches],
        "goleadores": list(goleadores or []),
    }


def _goals_for_team(match: Match, team: str, *, use_90: bool) -> tuple[int | None, int | None]:
    home_score = match.home_score_90 if use_90 else match.home_score
    away_score = match.away_score_90 if use_90 else match.away_score
    if match.home_team == team:
        return home_score, away_score
    return away_score, home_score


def _final_bonus(participant: ParticipantPick, meta: TournamentMeta) -> int:
    if meta.estado_torneo != "finalizado":
        return 0

    bonus = 0
    if participant.campeon == meta.campeon:
        bonus += BONUS_POINTS["campeon"]
    elif meta.campeon in participant.equipos:
        bonus += BONUS_POINTS["campeon_surprise"]

    if participant.subcampeon == meta.subcampeon:
        bonus += BONUS_POINTS["subcampeon"]

    if normalize_name(participant.pichichi) == normalize_name(meta.pichichi_nombre):
        bonus += BONUS_POINTS["pichichi"]

    return bonus


def _meta_from_any(meta: TournamentMeta | dict[str, Any]) -> TournamentMeta:
    if isinstance(meta, TournamentMeta):
        return meta
    return TournamentMeta(
        ultima_actualizacion=meta.get("ultima_actualizacion", ""),
        fuente=meta.get("fuente", "TheSportsDB liga 4429"),
        estado_torneo=meta.get("estado_torneo", "pre"),
        campeon=meta.get("campeon", ""),
        subcampeon=meta.get("subcampeon", ""),
        pichichi_nombre=meta.get("pichichi_nombre", ""),
        pichichi_goles=int(meta.get("pichichi_goles", 0)),
    )

