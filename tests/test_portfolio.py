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

    def test_mg_films_and_hotel_gray_stone_are_in_portfolio(self):
        source = (ROOT / "portfolio.html").read_text(encoding="utf-8")
        expected = {
            "MG Films Garage": "websites/screenshots/mg-films-garage.png",
            "Hotel Gray Stone": "websites/screenshots/hotel-gray-stone.png",
        }
        for title, screenshot in expected.items():
            with self.subTest(title=title):
                self.assertIn(f"<h3>{title}</h3>", source)
                self.assertIn(screenshot, source)

        mg_position = source.index("<h3>MG Films Garage</h3>")
        hotel_position = source.index("<h3>Hotel Gray Stone</h3>")
        first_legacy_position = source.index("<h3>Let&#x27;s Smile Dental</h3>")
        self.assertLess(mg_position, hotel_position)
        self.assertLess(hotel_position, first_legacy_position)

    def test_new_sample_screenshots_exist(self):
        for filename in ("mg-films-garage.png", "hotel-gray-stone.png"):
            with self.subTest(filename=filename):
                screenshot = ROOT / "websites" / "screenshots" / filename
                self.assertTrue(screenshot.is_file())
                self.assertGreater(screenshot.stat().st_size, 50_000)


if __name__ == "__main__":
    unittest.main()
