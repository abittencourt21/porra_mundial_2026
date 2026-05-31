import unittest
from unittest.mock import patch

from porra_mundial.build_data import _apply_overrides, _load_matches
from porra_mundial.models import Match


class BuildDataSportsDbTests(unittest.TestCase):
    def test_load_matches_prefers_sportsdb_when_available(self):
        payload = {
            "events": [
                {
                    "idEvent": "99",
                    "strHomeTeam": "Mexico",
                    "strAwayTeam": "South Africa",
                    "intRound": "1",
                    "intHomeScore": "2",
                    "intAwayScore": "1",
                    "dateEvent": "2026-06-11",
                    "strStatus": "FT",
                }
            ]
        }
        seed = {
            "partidos": [
                {
                    "matchid": 1,
                    "group": "A",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "11.06.2026",
                    "home_team": "Mexico",
                    "away_team": "Sudafrica",
                    "status": "NS",
                }
            ]
        }

        with patch("porra_mundial.build_data.fetch_world_cup_events", return_value=payload):
            matches, live_used = _load_matches(seed)

        self.assertTrue(live_used)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].home_team, "Mexico")
        self.assertEqual(matches[0].away_team, "Sudafrica")
        self.assertEqual(matches[0].home_score, 2)
        self.assertEqual(matches[0].away_score, 1)

    def test_load_matches_swaps_scores_when_sportsdb_orientation_differs(self):
        payload = {
            "events": [
                {
                    "idEvent": "99",
                    "strHomeTeam": "Mexico",
                    "strAwayTeam": "South Africa",
                    "intRound": "1",
                    "intHomeScore": "2",
                    "intAwayScore": "1",
                    "dateEvent": "2026-06-11",
                    "strStatus": "FT",
                }
            ]
        }
        seed = {
            "partidos": [
                {
                    "matchid": 1,
                    "group": "A",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "11.06.2026",
                    "home_team": "Sudafrica",
                    "away_team": "Mexico",
                    "status": "NS",
                }
            ]
        }

        with patch("porra_mundial.build_data.fetch_world_cup_events", return_value=payload):
            matches, live_used = _load_matches(seed)

        self.assertTrue(live_used)
        self.assertEqual(matches[0].home_score, 1)
        self.assertEqual(matches[0].away_score, 2)

    def test_load_matches_ignores_unmatched_sportsdb_event(self):
        payload = {
            "events": [
                {
                    "idEvent": "99",
                    "strHomeTeam": "Mexico",
                    "strAwayTeam": "South Africa",
                    "intHomeScore": "2",
                    "intAwayScore": "1",
                    "dateEvent": "2026-06-11",
                    "strStatus": "FT",
                }
            ]
        }
        seed = {
            "partidos": [
                {
                    "matchid": 1,
                    "group": "B",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "12.06.2026",
                    "home_team": "Espana",
                    "away_team": "Italia",
                    "status": "NS",
                }
            ]
        }

        with patch("porra_mundial.build_data.fetch_world_cup_events", return_value=payload):
            matches, live_used = _load_matches(seed)

        self.assertTrue(live_used)
        self.assertIsNone(matches[0].home_score)
        self.assertIsNone(matches[0].away_score)

    def test_apply_overrides_patches_match_meta_and_goleadores(self):
        matches = [
            Match(
                matchid=99,
                group="A",
                roundnumber=1,
                ronda="grupos",
                fecha="11.06.2026",
                home_team="Mexico",
                away_team="South Africa",
                status="NS",
            )
        ]
        overrides = [
            {
                "type": "match",
                "home_team": "Mexico",
                "away_team": "South Africa",
                "fecha": "11.06.2026",
                "home_score_90": "2",
                "away_score_90": "1",
                "pasa": "Mexico",
                "status": "FT",
            },
            {
                "type": "meta",
                "fuente": "Manual override",
                "estado_torneo": "grupos",
                "pichichi_goles": "7",
            },
            {
                "type": "goleador",
                "jugador": "Jugador Demo",
                "goles": "3",
            },
        ]

        patched_matches, patched_meta, goleadores = _apply_overrides(
            matches,
            overrides,
            {"fuente": "TheSportsDB liga 4429"},
            [],
        )

        self.assertEqual(patched_matches[0].home_score_90, 2)
        self.assertEqual(patched_matches[0].away_score_90, 1)
        self.assertEqual(patched_matches[0].pasa, "Mexico")
        self.assertEqual(patched_matches[0].status, "FT")
        self.assertEqual(patched_meta["fuente"], "Manual override")
        self.assertEqual(patched_meta["estado_torneo"], "grupos")
        self.assertEqual(patched_meta["pichichi_goles"], 7)
        self.assertEqual(goleadores, [{"jugador": "Jugador Demo", "goles": 3}])


if __name__ == "__main__":
    unittest.main()
