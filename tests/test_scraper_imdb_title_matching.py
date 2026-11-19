import unittest
from unittest.mock import patch

from src.scrapers.imdb_suggest import IMDB_SUGGEST


class TestIMDBSuggestTitleMatching(unittest.TestCase):

  @patch("src.scrapers.imdb_suggest.verify_config_file", return_value={})
  @patch("src.scrapers.imdb_suggest.requests.get")
  def test_exact_tv_special_beats_same_year_miniseries(self, request, _config):
    request.return_value.status_code = 200
    request.return_value.json.return_value = {"d": [
      {
        "id": "tt9145476",
        "l": "The Man",
        "qid": "tvMiniSeries",
        "y": 2019,
      },
      {
        "id": "tt10810424",
        "l": "Dave Chappelle: Sticks & Stones",
        "qid": "tvSpecial",
        "y": 2019,
      },
    ]}

    scraper = IMDB_SUGGEST("Dave Chappelle: Sticks & Stones (2019)")
    self.assertEqual("tt10810424", scraper.imdb_id)
