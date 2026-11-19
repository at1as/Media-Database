import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from src.series_refresh import merge_metadata
from src.worker import Worker


class TestSafeSeriesRefresh(unittest.TestCase):

  def setUp(self):
    self.saved = {
      "url": "http://www.imdb.com/title/tt1234567",
      "title": "Example",
      "info_retrieved": "2022-12-25",
      "year": "2017-2020",
      "creator": [],
      "description": "The original plot.",
      "stars": ["Saved Actor"],
      "rating": 8.2,
      "votes": 100,
      "directory": {"name": "Example (2017)", "absolute_path": "/media/Example"},
      "episodes": [{"Example S01E01": {"resolution": "1080p"}}],
    }
    self.fetched = {"url": "https://www.imdb.com/title/tt1234567/"}

  def test_improved_metadata_keeps_blank_and_local_fields(self):
    refreshed = merge_metadata(self.saved, {
      **self.fetched,
      "creator": ["New Creator"],
      "description": " ",
      "stars": [],
      "year": "2017",
      "rating": 8.0,
      "votes": 150,
      "genre": ["Drama"],
      "directory": {"absolute_path": None},
      "episodes": [],
    })

    self.assertEqual(refreshed["creator"], ["New Creator"])
    self.assertEqual(refreshed["genre"], ["Drama"])
    self.assertEqual(refreshed["rating"], 8.0)
    self.assertEqual(refreshed["votes"], 150)
    for field in ("description", "stars", "year", "directory", "episodes"):
      self.assertEqual(refreshed[field], self.saved[field])

  def test_different_title_or_no_improvement_is_rejected(self):
    self.assertIsNone(merge_metadata(self.saved, {
      "url": "https://www.imdb.com/title/tt7654321/",
      "creator": ["Wrong Creator"],
    }))
    self.assertIsNone(merge_metadata(self.saved, {
      **self.fetched, "votes": 0, "rating": 11, "description": " ",
    }))
    self.assertIsNone(merge_metadata(self.saved, {
      **self.fetched, "votes": "100", "rating": "8.2",
    }))

  def test_keeps_full_plot_when_refresh_returns_only_an_excerpt(self):
    saved = {**self.saved, "description": "A pilot finds a ship. The crew decides to land it."}
    refreshed = merge_metadata(saved, {
      **self.fetched, "description": "A pilot finds a ship…", "votes": 110,
    })
    self.assertEqual(refreshed["description"], saved["description"])

  def test_creator_lookup_failure_preserves_known_credits(self):
    saved = {**self.saved, "creator": ["Saved Creator"]}
    refreshed = merge_metadata(saved, {
      **self.fetched, "_creator_lookup_failed": True, "creator": ["Summary Creator"], "votes": 110,
    })
    self.assertEqual(refreshed["creator"], ["Saved Creator"])
    self.assertNotIn("_creator_lookup_failed", refreshed)

  def test_refresh_prioritizes_gaps_and_saves_timestamp_after_improvement(self):
    with tempfile.TemporaryDirectory() as folder:
      path = Path(folder) / "series.json"
      path.write_text(json.dumps({
        "Example (2017)": self.saved,
        "Complete (2000)": {**self.saved, "info_retrieved": "2000-01-01", "creator": ["Creator"]},
      }))
      worker = Worker.__new__(Worker)
      worker.config = {"assets": {"series": {"saved_data": str(path)}}}
      with patch("src.worker.scraper.Scraper") as scraper:
        scraper.return_value.get_series_details.return_value = {**self.fetched, "creator": ["New Creator"]}
        worker.refresh_series_entries(1)
      scraper.assert_called_once_with("IMDB_SUGGEST", "Example (2017)", "tt1234567")
      saved = json.loads(path.read_text())
      refreshed = saved["Example (2017)"]
      self.assertEqual(refreshed["creator"], ["New Creator"])
      timestamp = datetime.fromisoformat(refreshed["info_retrieved"])
      self.assertTrue(timestamp.tzinfo)
      self.assertGreater(worker.parse_info_retrieved(refreshed["info_retrieved"]),
                         worker.parse_info_retrieved("2022-12-25"))
      self.assertEqual(saved["Complete (2000)"]["info_retrieved"], "2000-01-01")

      before = path.read_bytes()
      with patch("src.worker.scraper.Scraper") as scraper:
        scraper.return_value.get_series_details.return_value = self.fetched
        worker.refresh_series_entries(2)
      self.assertEqual(path.read_bytes(), before)
