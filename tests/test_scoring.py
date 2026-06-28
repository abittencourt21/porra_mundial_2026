import unittest

from porra_mundial.scoring import build_datos_json, result_points, score_participant


class ScoringTests(unittest.TestCase):
    def test_result_points(self):
        self.assertEqual(result_points(2, 1), 3)
        self.assertEqual(result_points(1, 1), 1)
        self.assertEqual(result_points(0, 2), 0)
        self.assertEqual(result_points(None, 2), 0)

    def test_group_points_for_home_and_away_teams(self):
        participant = {
            "alias": "Ana",
            "equipos": ["Espana", "Brasil", "Marruecos", "Japon"],
            "campeon": "Espana",
            "subcampeon": "Brasil",
            "pichichi": "Alex",
        }
        matches = [
            {
                "matchid": 1,
                "ronda": "grupos",
                "fecha": "11.06.2026",
                "home_team": "Espana",
                "away_team": "Italia",
                "home_score": 2,
                "away_score": 1,
                "status": "FT",
            },
            {
                "matchid": 2,
                "ronda": "grupos",
                "fecha": "12.06.2026",
                "home_team": "Alemania",
                "away_team": "Brasil",
                "home_score": 0,
                "away_score": 0,
                "status": "FT",
            },
        ]
        scored = score_participant(participant, matches, _bombos(), {"ultima_actualizacion": ""})

        self.assertEqual(scored["desglose"]["grupos"], 4)
        self.assertEqual(scored["puntos_total"], 4)

    def test_playoff_uses_90_minute_score_and_pass_bonus(self):
        participant = {
            "alias": "Ana",
            "equipos": ["Espana", "Brasil", "Marruecos", "Japon"],
            "campeon": "Espana",
            "subcampeon": "Brasil",
            "pichichi": "Alex",
        }
        matches = [
            {
                "matchid": 73,
                "ronda": "R32",
                "fecha": "04.07.2026",
                "home_team": "Espana",
                "away_team": "Italia",
                "home_score": 2,
                "away_score": 1,
                "home_score_90": 1,
                "away_score_90": 1,
                "pasa": "Espana",
                "status": "FT",
            }
        ]
        scored = score_participant(participant, matches, _bombos(), {"ultima_actualizacion": ""})

        self.assertEqual(scored["desglose"]["playoffs_resultado"], 1)
        self.assertEqual(scored["desglose"]["playoffs_pase"], 1)
        self.assertEqual(scored["puntos_total"], 2)
        self.assertEqual(scored["team_data"][0]["rondas_pasadas"], ["R32"])

    def test_reaching_r32_awards_bombo_bonus_before_match_is_played(self):
        participant = {
            "alias": "Ana",
            "equipos": ["Espana", "Brasil", "Marruecos", "Japon"],
            "campeon": "Espana",
            "subcampeon": "Brasil",
            "pichichi": "Alex",
        }
        matches = [
            {
                "matchid": 73,
                "ronda": "R32",
                "fecha": "28.06.2026",
                "home_team": "Japon",
                "away_team": "Italia",
                "home_score": None,
                "away_score": None,
                "home_score_90": None,
                "away_score_90": None,
                "pasa": None,
                "status": "NS",
            }
        ]

        scored = score_participant(participant, matches, _bombos(), {"ultima_actualizacion": ""})

        self.assertEqual(scored["desglose"]["playoffs_resultado"], 0)
        self.assertEqual(scored["desglose"]["playoffs_pase"], 4)
        self.assertEqual(scored["team_data"][3]["rondas_pasadas"], ["R32"])

        scored_duplicate = score_participant(
            participant,
            matches + [{**matches[0], "matchid": 74}],
            _bombos(),
            {"ultima_actualizacion": ""},
        )
        self.assertEqual(scored_duplicate["desglose"]["playoffs_pase"], 4)

    def test_third_place_match_does_not_score_or_count_as_round_passed(self):
        participant = {
            "alias": "Ana",
            "equipos": ["Espana", "Brasil", "Marruecos", "Japon"],
            "campeon": "Espana",
            "subcampeon": "Brasil",
            "pichichi": "Alex",
        }
        matches = [
            {
                "matchid": 103,
                "ronda": "3RD",
                "fecha": "18.07.2026",
                "home_team": "Espana",
                "away_team": "Brasil",
                "home_score": 2,
                "away_score": 1,
                "home_score_90": 2,
                "away_score_90": 1,
                "pasa": "Espana",
                "status": "FT",
            }
        ]

        scored = score_participant(participant, matches, _bombos(), {"ultima_actualizacion": ""})

        self.assertEqual(scored["desglose"]["playoffs_resultado"], 0)
        self.assertEqual(scored["desglose"]["playoffs_pase"], 0)
        self.assertEqual(scored["puntos_total"], 0)
        self.assertEqual(scored["team_data"][0]["rondas_pasadas"], [])

    def test_final_bonus(self):
        participant = {
            "alias": "Ana",
            "equipos": ["Espana", "Brasil", "Marruecos", "Japon"],
            "campeon": "Brasil",
            "subcampeon": "Espana",
            "pichichi": "Alex Morgan",
        }
        meta = {
            "ultima_actualizacion": "",
            "estado_torneo": "finalizado",
            "campeon": "Espana",
            "subcampeon": "Espana",
            "pichichi_nombre": "alex   morgan",
        }
        scored = score_participant(participant, [], _bombos(), meta)

        self.assertEqual(scored["desglose"]["bonus_final"], 18)

    def test_build_ranking_orders_by_points_then_alias(self):
        participants = [
            {"alias": "Beto", "equipos": ["Espana", "Brasil", "Marruecos", "Japon"]},
            {"alias": "Ana", "equipos": ["Francia", "Argentina", "Ghana", "Canada"]},
        ]
        matches = [
            {
                "matchid": 1,
                "ronda": "grupos",
                "fecha": "11.06.2026",
                "home_team": "Francia",
                "away_team": "Italia",
                "home_score": 1,
                "away_score": 0,
            }
        ]
        payload = build_datos_json(participants, matches, _bombos())

        self.assertEqual(payload["participantes"][0]["alias"], "Ana")


def _bombos():
    return {
        "Espana": 1,
        "Francia": 1,
        "Brasil": 2,
        "Argentina": 2,
        "Marruecos": 3,
        "Ghana": 3,
        "Japon": 4,
        "Canada": 4,
    }


if __name__ == "__main__":
    unittest.main()
