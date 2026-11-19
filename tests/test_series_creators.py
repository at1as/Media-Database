import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from imdbinfo import GraphQLError

from src.scraper import Scraper
from src.worker import Worker


class TestSeriesCreators(unittest.TestCase):

  def setUp(self):
    with patch('src.scrapers.imdb_suggest.verify_config_file', return_value={'pause_time_sec': 0}):
      self.scraper = Scraper('IMDB_SUGGEST', 'Example Series', foreign_id='tt1234567')
    detail_patcher = patch('src.scrapers.imdb_suggest.imdbinfo_get_movie', return_value={
      'title': 'Example Series',
      'year': 2025,
      'plot': 'An example plot.',
      'directors': [{'name': 'A Director'}],
      'info_series': {'creators': [{'name': 'First Creator'}]},
    })
    self.detail = detail_patcher.start().return_value
    self.addCleanup(detail_patcher.stop)

  @patch('src.scrapers.imdb_suggest.get_series_creators')
  def test_series_combines_full_and_summary_creators(self, full_credits):
    full_credits.return_value = [{'name': 'First Creator'}, {'name': 'Second Creator'}]

    result = self.scraper.get_series_details(None, None)

    full_credits.assert_called_once_with('tt1234567')
    self.assertEqual(result['creator'], ['First Creator', 'Second Creator'])
    self.assertEqual(result['description'], 'An example plot.')
    self.assertNotIn('_creator_lookup_failed', result)

  @patch('src.scrapers.imdb_suggest.get_series_creators', return_value=[])
  def test_empty_creator_credits_do_not_use_directors(self, full_credits):
    self.detail['info_series'] = {}

    result = self.scraper.get_series_details(None, None)

    full_credits.assert_called_once_with('tt1234567')
    self.assertEqual(result['creator'], [])
    self.assertEqual(result['director'], ['A Director'])

  @patch('src.scrapers.imdb_suggest.get_series_creators')
  def test_movies_and_standup_do_not_request_creator_credits(self, full_credits):
    self.scraper.get_movie_details(None, None)
    self.scraper.get_standup_details(None, None)

    full_credits.assert_not_called()

  @patch(
    'src.scrapers.imdb_suggest.get_series_creators',
    side_effect=GraphQLError('Unavailable', url='https://example.com/', query_term='tt1234567'),
  )
  def test_failed_lookup_preserves_saved_creators_and_uses_summary_for_new_titles(self, full_credits):
    scraped = self.scraper.get_series_details(None, None)
    self.assertEqual(scraped['creator'], ['First Creator'])
    self.assertTrue(scraped['_creator_lookup_failed'])

    with tempfile.TemporaryDirectory() as temp_dir:
      path = Path(temp_dir) / 'series.json'
      path.write_text(json.dumps({'Existing Series': {'creator': ['Previously Saved']}}))
      worker = Worker.__new__(Worker)
      worker.config = {'assets': {'series': {'saved_data': str(path)}}}
      worker.write_scraped_data('series', [
        {**scraped, 'directory': {'name': 'Existing Series'}},
        {**scraped, 'directory': {'name': 'New Series'}},
      ])
      saved = json.loads(path.read_text())

    full_credits.assert_called_once_with('tt1234567')
    self.assertEqual(saved['Existing Series']['creator'], ['Previously Saved'])
    self.assertEqual(saved['New Series']['creator'], ['First Creator'])
    self.assertNotIn('_creator_lookup_failed', saved['Existing Series'])
    self.assertNotIn('_creator_lookup_failed', saved['New Series'])
