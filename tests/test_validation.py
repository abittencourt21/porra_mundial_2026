import unittest

from porra_mundial.validation import find_combination_conflicts


class ValidationTests(unittest.TestCase):
    def test_detects_three_shared_teams_and_keeps_earliest_timestamp(self):
        participants = [
            {
                "alias": "Primero",
                "timestamp": "2026-05-01T10:00:00",
                "equipos": ["Espana", "Brasil", "Marruecos", "Japon"],
            },
            {
                "alias": "Segundo",
                "timestamp": "2026-05-01T10:01:00",
                "equipos": ["Espana", "Brasil", "Marruecos", "Canada"],
            },
        ]

        conflicts = find_combination_conflicts(participants)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["winner"], "Primero")
        self.assertEqual(conflicts[0]["loser"], "Segundo")
        self.assertEqual(conflicts[0]["intersection"], 3)

    def test_allows_two_shared_teams(self):
        participants = [
            {"alias": "A", "equipos": ["Espana", "Brasil", "Marruecos", "Japon"]},
            {"alias": "B", "equipos": ["Espana", "Brasil", "Ghana", "Canada"]},
        ]

        self.assertEqual(find_combination_conflicts(participants), [])


if __name__ == "__main__":
    unittest.main()
