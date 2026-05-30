"""Motor de la porra del Mundial 2026."""

from .scoring import build_datos_json, score_participant
from .validation import find_combination_conflicts

__all__ = ["build_datos_json", "score_participant", "find_combination_conflicts"]

