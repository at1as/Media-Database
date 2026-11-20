import unittest

from src.scrapers.imdb_suggest import IMDB_SUGGEST


class TestIMDBSuggestContentRating(unittest.TestCase):

  def setUp(self):
    self.scraper = IMDB_SUGGEST.__new__(IMDB_SUGGEST)

  def test_normalizes_self_applied_certificate_suffix(self):
    value = self.scraper._IMDB_SUGGEST__content_rating_from_imdbinfo({
      "mpaa": "TV-MA self-applied"
    })

    self.assertEqual("TV-MA", value)

  def test_normalizes_certificate_suffixes(self):
    value = self.scraper._IMDB_SUGGEST__content_rating_from_imdbinfo({
      "certificates": {
        "US": "TV-MA certificate #12345 self-applied"
      }
    })

    self.assertEqual("TV-MA", value)
