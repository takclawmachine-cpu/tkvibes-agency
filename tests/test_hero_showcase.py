import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class HeroShowcaseContractTests(unittest.TestCase):
    def test_latest_portfolio_samples_lead_hero_orbit(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        cards = re.findall(r'<article class="orbit-card".*?</article>', source, re.S)
        self.assertEqual(len(cards), 7)
        self.assertIn("MG Films Garage", cards[0])
        self.assertIn("websites/screenshots/mg-films-garage.png", cards[0])
        self.assertIn("Hotel Gray Stone", cards[1])
        self.assertIn("websites/screenshots/hotel-gray-stone.png", cards[1])


if __name__ == "__main__":
    unittest.main()
