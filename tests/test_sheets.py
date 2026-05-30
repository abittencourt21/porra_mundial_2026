import unittest
from unittest.mock import patch

from porra_mundial.sheets import _read_tsv_url, _rows_to_dicts, _sanitize_participant


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

    def test_reads_public_tsv_url(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return "Alias\tEquipo del Bombo 1\nCrack26\tEspana\n".encode()

        with patch("porra_mundial.sheets.urlopen", return_value=FakeResponse()):
            rows = _read_tsv_url("https://example.test/public.tsv")

        self.assertEqual(rows, [["Alias", "Equipo del Bombo 1"], ["Crack26", "Espana"]])

    def test_sanitizes_current_public_tsv_headers(self):
        values = [
            [
                "Marca temporal",
                "Alias público",
                "Bombo 1",
                "Bombo 2",
                "Bombo 3",
                "Bombo 4",
                "Campeón",
                "Subcampeón",
                "Bota de oro",
            ],
            [
                "30/05/2026 23:40:51",
                "Allan",
                "Brasil",
                "Colombia",
                "Egipto",
                "Chequia",
                "Brasil",
                "España",
                "Harry Kane",
            ],
        ]

        row = _rows_to_dicts(values)[0]
        participant = _sanitize_participant(row)

        self.assertEqual(participant["alias"], "Allan")
        self.assertEqual(participant["equipos"], ["Brasil", "Colombia", "Egipto", "Chequia"])
        self.assertEqual(participant["campeon"], "Brasil")
        self.assertEqual(participant["subcampeon"], "España")
        self.assertEqual(participant["pichichi"], "Harry Kane")


if __name__ == "__main__":
    unittest.main()
