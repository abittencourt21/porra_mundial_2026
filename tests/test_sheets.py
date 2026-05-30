import unittest

from porra_mundial.sheets import _rows_to_dicts, _sanitize_participant


class SheetMappingTests(unittest.TestCase):
    def test_sanitizes_google_form_row_without_private_fields(self):
        values = [
            [
                "Marca temporal",
                "Nombre real",
                "Email",
                "Alias",
                "Equipo del Bombo 1",
                "Equipo del Bombo 2",
                "Equipo del Bombo 3",
                "Equipo del Bombo 4",
                "Campeon",
                "Subcampeon",
                "Pichichi",
                "Pagado",
            ],
            [
                "2026-06-01 10:00",
                "Persona Privada",
                "privado@example.com",
                "Crack26",
                "Espana",
                "Brasil",
                "Marruecos",
                "Japon",
                "Espana",
                "Brasil",
                "Jugador Demo",
                "si",
            ],
        ]

        row = _rows_to_dicts(values)[0]
        participant = _sanitize_participant(row)

        self.assertEqual(participant["alias"], "Crack26")
        self.assertEqual(participant["equipos"], ["Espana", "Brasil", "Marruecos", "Japon"])
        self.assertTrue(participant["pagado"])
        self.assertNotIn("Nombre real", participant)
        self.assertNotIn("Email", participant)


if __name__ == "__main__":
    unittest.main()

