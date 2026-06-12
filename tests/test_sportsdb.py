import unittest

from porra_mundial.sportsdb import parse_event, summarize_payload


class SportsDbTests(unittest.TestCase):
    def test_parse_event_maps_basic_fields(self):
        match = parse_event(
            {
                "idEvent": "2391728",
                "strHomeTeam": "Mexico",
                "strAwayTeam": "South Africa",
                "intRound": "1",
                "intHomeScore": None,
                "intAwayScore": None,
                "dateEvent": "2026-06-11",
                "strStatus": "NS",
            }
        )

        self.assertEqual(match.matchid, 2391728)
        self.assertEqual(match.ronda, "grupos")
        self.assertEqual(match.roundnumber, 1)
        self.assertEqual(match.fecha, "11.06.2026")
        self.assertEqual(match.home_team, "Mexico")
        self.assertEqual(match.away_team, "South Africa")
        self.assertIsNone(match.home_score)
        self.assertEqual(match.status, "NS")

    def test_parse_event_prefers_local_date_and_keeps_group_round(self):
        match = parse_event(
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
                "strDescriptionEN": "The match changed in the middle third.",
                "strStatus": "FT",
            }
        )

        self.assertEqual(match.fecha, "11.06.2026")
        self.assertEqual(match.ronda, "grupos")
        self.assertEqual(match.group, "A")
        self.assertEqual(match.home_score, 2)
        self.assertEqual(match.away_score, 1)

    def test_summarize_payload_reports_api_shape(self):
        summary = summarize_payload(
            {
                "events": [
                    {"idEvent": "1", "intRound": "1", "strStatus": "NS", "strEvent": "A vs B"},
                    {"idEvent": "2", "intRound": "1", "strStatus": "FT", "strEvent": "C vs D"},
                ]
            }
        )

        self.assertEqual(summary["event_count"], 2)
        self.assertEqual(summary["rounds"], {"1": 2})
        self.assertEqual(summary["statuses"], {"FT": 1, "NS": 1})
        self.assertIn("strEvent", summary["keys"])


if __name__ == "__main__":
    unittest.main()
