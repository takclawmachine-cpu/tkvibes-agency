import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PortfolioContractTests(unittest.TestCase):
    def test_winston_churchill_dental_is_linked_in_portfolio(self):
        source = (ROOT / "portfolio.html").read_text(encoding="utf-8")
        self.assertIn("Winston Churchill Dental", source)
        self.assertIn("https://winston-churchill-dental.tkvibes.in/", source)
        self.assertIn("websites/screenshots/winston-churchill-dental.png", source)

    def test_winston_portfolio_screenshot_exists(self):
        screenshot = ROOT / "websites" / "screenshots" / "winston-churchill-dental.png"
        self.assertTrue(screenshot.is_file())
        self.assertGreater(screenshot.stat().st_size, 50_000)


if __name__ == "__main__":
    unittest.main()
