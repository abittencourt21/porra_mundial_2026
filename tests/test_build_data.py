import unittest
from unittest.mock import call, patch

from porra_mundial.build_data import _apply_overrides, _enrich_ranking, _load_matches, _team_key
from porra_mundial.models import Match


class BuildDataSportsDbTests(unittest.TestCase):
    def test_team_key_matches_spanish_accents_and_sportsdb_names(self):
        cases = {
            "España": "Spain",
            "México": "Mexico",
            "Canadá": "Canada",
            "Bélgica": "Belgium",
            "Países Bajos": "Netherlands",
            "Panamá": "Panama",
            "Túnez": "Tunisia",
            "Arabia Saudí": "Saudi Arabia",
            "Sudáfrica": "South Africa",
            "Turquía": "Türkiye",
            "Uzbekistán": "Uzbekistan",
            "Curazao": "Curaçao",
            "Costa de Marfil": "Côte d’Ivoire",
            "RD Congo": "Congo DR",
            "Estados Unidos": "United States of America",
        }

        for spanish_name, sportsdb_name in cases.items():
            with self.subTest(spanish_name=spanish_name, sportsdb_name=sportsdb_name):
                self.assertEqual(_team_key(spanish_name), _team_key(sportsdb_name))

    def test_load_matches_pairs_accented_seed_names_with_sportsdb_variants(self):
        payload = {
            "events": [
                {
                    "idEvent": "99",
                    "strHomeTeam": "Spain",
                    "strAwayTeam": "Côte d’Ivoire",
                    "intRound": "1",
                    "intHomeScore": "2",
                    "intAwayScore": "1",
                    "dateEvent": "2026-06-15",
                    "strStatus": "FT",
                }
            ]
        }
        seed = {
            "partidos": [
                {
                    "matchid": 13,
                    "group": "H",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "15.06.2026",
                    "home_team": "España",
                    "away_team": "Costa de Marfil",
                    "status": "NS",
                }
            ]
        }

        with patch(
            "porra_mundial.build_data.fetch_world_cup_events_for_date",
            side_effect=[{"events": []}, {"events": []}, payload],
        ):
            matches, live_used, alerts = _load_matches(seed, build_date="2026-06-15")

        self.assertTrue(live_used)
        self.assertEqual(alerts, [])
        self.assertEqual(matches[0].home_score, 2)
        self.assertEqual(matches[0].away_score, 1)

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

        with patch(
            "porra_mundial.build_data.fetch_world_cup_events_for_date",
            side_effect=[{"events": []}, {"events": []}, payload],
        ) as fetch:
            matches, live_used, alerts = _load_matches(seed, build_date="2026-06-11")

        fetch.assert_has_calls([call("2026-06-09"), call("2026-06-10"), call("2026-06-11")])
        self.assertTrue(live_used)
        self.assertEqual(alerts, [])
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

        with patch(
            "porra_mundial.build_data.fetch_world_cup_events_for_date",
            side_effect=[{"events": []}, {"events": []}, payload],
        ):
            matches, live_used, alerts = _load_matches(seed, build_date="2026-06-11")

        self.assertTrue(live_used)
        self.assertEqual(alerts, [])
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
                    "dateEvent": "2026-06-12",
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

        with patch(
            "porra_mundial.build_data.fetch_world_cup_events_for_date",
            side_effect=[{"events": []}, {"events": []}, payload],
        ):
            matches, live_used, alerts = _load_matches(seed, build_date="2026-06-12")

        self.assertTrue(live_used)
        self.assertEqual(len(alerts), 2)
        self.assertIsNone(matches[0].home_score)
        self.assertIsNone(matches[0].away_score)

    def test_load_matches_fetches_previous_day_for_midnight_boundary(self):
        payload_previous_day = {
            "events": [
                {
                    "idEvent": "99",
                    "strHomeTeam": "Brazil",
                    "strAwayTeam": "Morocco",
                    "intRound": "1",
                    "intHomeScore": "3",
                    "intAwayScore": "1",
                    "dateEvent": "2026-06-13",
                    "strStatus": "FT",
                }
            ]
        }
        seed = {
            "partidos": [
                {
                    "matchid": 1,
                    "group": "C",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "13.06.2026",
                    "home_team": "Brasil",
                    "away_team": "Marruecos",
                    "status": "NS",
                }
            ]
        }

        with patch(
            "porra_mundial.build_data.fetch_world_cup_events_for_date",
            side_effect=[{"events": []}, payload_previous_day, {"events": []}],
        ) as fetch:
            matches, live_used, alerts = _load_matches(seed, build_date="2026-06-14")

        fetch.assert_has_calls([call("2026-06-12"), call("2026-06-13"), call("2026-06-14")])
        self.assertTrue(live_used)
        self.assertEqual(alerts, [])
        self.assertEqual(matches[0].home_score, 3)
        self.assertEqual(matches[0].away_score, 1)

    def test_load_matches_uses_sportsdb_local_date_for_matching(self):
        payload_next_utc_day = {
            "events": [
                {
                    "idEvent": "2461103",
                    "strHomeTeam": "South Korea",
                    "strAwayTeam": "Czech Republic",
                    "intRound": "1",
                    "intHomeScore": "2",
                    "intAwayScore": "1",
                    "dateEvent": "2026-06-12",
                    "dateEventLocal": "2026-06-11",
                    "strGroup": "A",
                    "strStatus": "FT",
                }
            ]
        }
        seed = {
            "partidos": [
                {
                    "matchid": 2,
                    "group": "A",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "11.06.2026",
                    "home_team": "Corea del Sur",
                    "away_team": "Chequia",
                    "status": "NS",
                }
            ]
        }

        with patch(
            "porra_mundial.build_data.fetch_world_cup_events_for_date",
            side_effect=[{"events": []}, {"events": []}, payload_next_utc_day],
        ) as fetch:
            matches, live_used, alerts = _load_matches(seed, build_date="2026-06-12")

        fetch.assert_has_calls([call("2026-06-10"), call("2026-06-11"), call("2026-06-12")])
        self.assertTrue(live_used)
        self.assertEqual(alerts, [])
        self.assertEqual(matches[0].fecha, "11.06.2026")
        self.assertEqual(matches[0].home_score, 2)
        self.assertEqual(matches[0].away_score, 1)

    def test_load_matches_keeps_previous_scores_for_past_days(self):
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
                },
                {
                    "matchid": 2,
                    "group": "A",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "15.06.2026",
                    "home_team": "Espana",
                    "away_team": "Italia",
                    "status": "NS",
                },
            ]
        }
        previous = {
            "partidos": [
                {
                    "matchid": 1,
                    "group": "A",
                    "roundnumber": 1,
                    "ronda": "grupos",
                    "fecha": "11.06.2026",
                    "home_team": "Mexico",
                    "away_team": "Sudafrica",
                    "home_score": 2,
                    "away_score": 1,
                    "home_score_90": 2,
                    "away_score_90": 1,
                    "status": "FT",
                }
            ]
        }
        payload = {"events": []}

        with patch("porra_mundial.build_data.fetch_world_cup_events_for_date", return_value=payload):
            matches, live_used, alerts = _load_matches(seed, previous, build_date="2026-06-15")

        self.assertFalse(live_used)
        self.assertEqual(matches[0].home_score, 2)
        self.assertEqual(matches[0].away_score, 1)
        self.assertIsNone(matches[1].home_score)
        self.assertEqual(len(alerts), 1)

    def test_load_matches_does_not_call_sportsdb_without_today_matches(self):
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

        with patch("porra_mundial.build_data.fetch_world_cup_events_for_date") as fetch:
            matches, live_used, alerts = _load_matches(seed, build_date="2026-06-15")

        fetch.assert_not_called()
        self.assertFalse(live_used)
        self.assertEqual(alerts, [])
        self.assertEqual(len(matches), 1)

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

    def test_enrich_ranking_adds_deltas_and_history(self):
        payload = {
            "meta": {},
            "participantes": [
                {"alias": "B", "puntos_total": 7},
                {"alias": "A", "puntos_total": 5},
            ],
            "partidos": [],
        }
        previous = {
            "meta": {
                "ranking_history": [
                    {
                        "checkpoint": "pre",
                        "label": "Pre",
                        "fecha": "2026-06-01",
                        "alias": "A",
                        "posicion": 1,
                        "puntos": 0,
                    }
                ]
            },
            "participantes": [
                {"alias": "A", "rank_actual": 1},
                {"alias": "B", "rank_actual": 2},
            ],
        }

        _enrich_ranking(payload, previous, "2026-06-15")

        self.assertEqual(payload["participantes"][0]["rank_actual"], 1)
        self.assertEqual(payload["participantes"][0]["rank_anterior"], 2)
        self.assertEqual(payload["participantes"][0]["rank_delta"], 1)
        self.assertEqual(payload["participantes"][0]["rank_status"], "sube")
        self.assertEqual(payload["participantes"][1]["rank_status"], "baja")
        self.assertEqual(
            {row["alias"] for row in payload["meta"]["ranking_history"] if row["checkpoint"] == "pre"},
            {"A", "B"},
        )


if __name__ == "__main__":
    unittest.main()
