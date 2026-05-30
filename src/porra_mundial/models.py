from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


GROUP_ROUND = "grupos"
KO_ROUNDS = ("R32", "R16", "QF", "SF", "F")


@dataclass(frozen=True)
class Match:
    matchid: int
    group: str | None
    roundnumber: int | None
    ronda: str
    fecha: str
    home_team: str
    away_team: str
    home_score: int | None = None
    away_score: int | None = None
    home_score_90: int | None = None
    away_score_90: int | None = None
    pasa: str | None = None
    status: str = "NS"

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Match":
        return cls(
            matchid=int(raw.get("matchid", 0)),
            group=raw.get("group"),
            roundnumber=raw.get("roundnumber"),
            ronda=raw["ronda"],
            fecha=raw.get("fecha", ""),
            home_team=raw.get("home_team", ""),
            away_team=raw.get("away_team", ""),
            home_score=raw.get("home_score"),
            away_score=raw.get("away_score"),
            home_score_90=raw.get("home_score_90"),
            away_score_90=raw.get("away_score_90"),
            pasa=raw.get("pasa"),
            status=raw.get("status", "NS"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "matchid": self.matchid,
            "group": self.group,
            "roundnumber": self.roundnumber,
            "ronda": self.ronda,
            "fecha": self.fecha,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "home_score_90": self.home_score_90,
            "away_score_90": self.away_score_90,
            "pasa": self.pasa,
            "status": self.status,
        }


@dataclass(frozen=True)
class ParticipantPick:
    alias: str
    equipos: tuple[str, str, str, str]
    campeon: str
    subcampeon: str
    pichichi: str
    pagado: bool = False
    timestamp: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ParticipantPick":
        equipos = tuple(raw.get("equipos", ()))
        if len(equipos) != 4:
            raise ValueError(f"{raw.get('alias', '<sin alias>')} debe tener 4 equipos")
        return cls(
            alias=raw["alias"],
            equipos=equipos,  # type: ignore[arg-type]
            campeon=raw.get("campeon", ""),
            subcampeon=raw.get("subcampeon", ""),
            pichichi=raw.get("pichichi", ""),
            pagado=bool(raw.get("pagado", False)),
            timestamp=raw.get("timestamp", ""),
        )


@dataclass
class TournamentMeta:
    ultima_actualizacion: str
    fuente: str = "TheSportsDB liga 4429"
    estado_torneo: str = "pre"
    campeon: str = ""
    subcampeon: str = ""
    pichichi_nombre: str = ""
    pichichi_goles: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ultima_actualizacion": self.ultima_actualizacion,
            "fuente": self.fuente,
            "estado_torneo": self.estado_torneo,
            "campeon": self.campeon,
            "subcampeon": self.subcampeon,
            "pichichi_nombre": self.pichichi_nombre,
            "pichichi_goles": self.pichichi_goles,
        }


@dataclass
class TeamScore:
    team: str
    bombo: int
    g_pts: int = 0
    ko_result_pts: int = 0
    ko_pass_pts: int = 0
    rondas_pasadas: list[str] = field(default_factory=list)
    ko_det: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ko_pts(self) -> int:
        return self.ko_result_pts + self.ko_pass_pts

    def to_dict(self) -> dict[str, Any]:
        return {
            "team": self.team,
            "bombo": self.bombo,
            "g_pts": self.g_pts,
            "ko_pts": self.ko_pts,
            "rondas_pasadas": self.rondas_pasadas,
            "ko_det": self.ko_det,
        }

