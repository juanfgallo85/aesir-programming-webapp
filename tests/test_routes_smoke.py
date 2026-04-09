import subprocess
import sys
import unittest
from pathlib import Path

from app import create_app
from app.services.data_loader import (
    load_all_sessions,
    load_blocks,
    load_glossary,
    load_movements,
    load_weeks,
)


BASE_DIR = Path(__file__).resolve().parents[1]


class RouteSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_main_routes_return_200(self):
        routes = [
            "/",
            "/today",
            "/calendar",
            "/week/current",
            "/week/2026-04-06",
            "/block/current",
            "/library",
            "/glossary",
            "/day/2026-04-08",
            "/export/day/2026-04-08",
            "/export/week/2026-04-06",
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)


class DataLoaderSmokeTests(unittest.TestCase):
    def test_loaders_handle_expanded_content(self):
        self.assertGreaterEqual(len(load_blocks()), 13)
        self.assertGreaterEqual(len(load_weeks()), 52)
        self.assertGreaterEqual(len(load_movements()), 40)
        self.assertGreaterEqual(len(load_glossary()), 30)
        self.assertGreaterEqual(len(load_all_sessions()), 48)

    def test_validate_data_script_runs_clean(self):
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "scripts" / "validate_data.py")],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("OK all sessions:", result.stdout)
        self.assertIn("OK movements:", result.stdout)
        self.assertIn("OK glossary terms:", result.stdout)


if __name__ == "__main__":
    unittest.main()
