import csv
import unittest
from pathlib import Path

from porra_mundial.overrides_template import build_overrides_template_rows


ROOT = Path(__file__).resolve().parents[1]


class OverridesTemplateTests(unittest.TestCase):
    def test_template_has_safe_editable_match_rows(self):
        template_path = ROOT / "data" / "overrides_template.csv"

        with template_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        match_rows = [row for row in rows if row["type"] == "match"]

        self.assertEqual(len(match_rows), 72)
        self.assertIn("matchid", match_rows[0])
        self.assertIn("home_score_90", match_rows[0])
        self.assertIn("away_score_90", match_rows[0])
        self.assertIn("pasa", match_rows[0])
        self.assertTrue(all(row["home_score"] == "" for row in match_rows))
        self.assertTrue(all(row["away_score"] == "" for row in match_rows))
        self.assertTrue(all(row["status"] == "" for row in match_rows))

    def test_generator_keeps_scores_blank_by_default(self):
        seed = {
            "meta": {"estado_torneo": "pre"},
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
                    "status": "FT",
                }
            ],
        }

        rows = build_overrides_template_rows(seed)
        match_row = next(row for row in rows if row["type"] == "match")

        self.assertEqual(match_row["matchid"], 1)
        self.assertEqual(match_row["home_score"], "")
        self.assertEqual(match_row["away_score"], "")
        self.assertEqual(match_row["status"], "")


if __name__ == "__main__":
    unittest.main()
