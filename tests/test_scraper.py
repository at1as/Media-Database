import unittest
from unittest.mock import patch

from src.scraper import Scraper
from src.scrapers.imdb_suggest import IMDB_SUGGEST


class TestScraper(unittest.TestCase):

  @patch("src.scrapers.imdb_suggest.verify_config_file", return_value={})
  def test_imdb_suggestion_source_uses_the_supplied_id(self, _config):
    scraper = Scraper("IMDB_SUGGEST", "Example", "tt1234567")
    self.assertIsInstance(scraper, IMDB_SUGGEST)
    self.assertEqual(scraper.imdb_id, "tt1234567")

  @patch("src.scrapers.imdb_suggest.verify_config_file", return_value={})
  def test_unknown_source_falls_back_to_imdb_suggestions(self, _config):
    scraper = Scraper("SCRAPER_DOES_NOT_EXIST", "Example", "tt1234567")
    self.assertIsInstance(scraper, IMDB_SUGGEST)

  def test_tmdb_reports_that_it_is_unimplemented(self):
    with self.assertRaises(NotImplementedError):
      Scraper("TMDB")
