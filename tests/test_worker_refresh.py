import json
import os
import tempfile
import unittest

from src.worker import Worker


class TestWorkerRefresh(unittest.TestCase):

  def build_worker(self, saved_data_path, location="/library/"):
    worker = Worker.__new__(Worker)
    worker.config = {
      "assets": {
        "movies": {
          "saved_data": saved_data_path,
          "location": location,
        },
        "series": {
          "saved_data": saved_data_path,
          "location": location,
        },
        "standup": {
          "saved_data": saved_data_path,
          "location": location,
        },
      }
    }
    worker.series_scraper = None
    worker.movie_scraper = None
    return worker

  def write_saved_data(self, payload):
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
    try:
      json.dump(payload, handle)
      handle.close()
      return handle.name
    except Exception:
      handle.close()
      os.unlink(handle.name)
      raise

  def test_get_refresh_candidates_sorts_oldest_entries_first(self):
    saved_data_path = self.write_saved_data({
      "Movie C": {
        "info_retrieved": "2024-04-01",
        "file_metadata": {
          "filename": "Movie C",
          "extension": "mkv",
          "absolute_path": "/library/Movie C.mkv",
          "relative_path": "Movie C.mkv",
        }
      },
      "Movie A": {
        "info_retrieved": "2021-01-02",
        "file_metadata": {
          "filename": "Movie A",
          "extension": "mp4",
          "absolute_path": "/library/Movie A.mp4",
          "relative_path": "Movie A.mp4",
        }
      },
      "Movie B": {
        "info_retrieved": "2022-03-04",
        "file_metadata": {
          "filename": "Movie B",
          "extension": "avi",
          "absolute_path": "/library/Movie B.avi",
          "relative_path": "Movie B.avi",
        }
      }
    })

    try:
      worker = self.build_worker(saved_data_path)
      refresh_candidates = worker.get_refresh_candidates("movies", "movie", 2)
    finally:
      os.unlink(saved_data_path)

    self.assertEqual(["Movie A", "Movie B"], [x["name"] for x in refresh_candidates])
    self.assertEqual(["Movie A.mp4", "Movie B.avi"], [x["relative_path"] for x in refresh_candidates])

  def test_build_refresh_file_details_falls_back_to_asset_name_for_series(self):
    worker = self.build_worker("/tmp/unused.json")
    file_details = worker.build_refresh_file_details(
      "/library/",
      "Series A",
      {
        "directory": {
          "name": "Series A",
          "absolute_path": None,
          "relative_path": None,
        }
      },
      "series"
    )

    self.assertEqual("Series A", file_details["name"])
    self.assertEqual("Series A", file_details["relative_path"])
    self.assertEqual("/library/Series A", file_details["full_path"])

  def test_build_refresh_file_details_prefers_conf_path_over_stale_absolute_path(self):
    temp_dir = tempfile.mkdtemp()
    media_file = os.path.join(temp_dir, "Ali Wong Don Wong (2022).mp4")

    try:
      with open(media_file, "w") as handle:
        handle.write("x")

      worker = self.build_worker("/tmp/unused.json")
      file_details = worker.build_refresh_file_details(
        temp_dir,
        "Ali Wong Don Wong (2022)",
        {
          "file_metadata": {
            "filename": "Ali Wong Don Wong (2022)",
            "extension": "mp4",
            "absolute_path": "/test-media/standup/Ali Wong Don Wong (2022).mp4",
            "relative_path": "Ali Wong Don Wong (2022).mp4",
          }
        },
        "standup"
      )
    finally:
      os.unlink(media_file)
      os.rmdir(temp_dir)

    self.assertEqual(media_file, file_details["full_path"])

  def test_write_scraped_data_merges_refreshed_asset_with_existing_fields(self):
    saved_data_path = self.write_saved_data({
      "Movie A": {
        "custom_note": "keep me",
        "info_retrieved": "2020-01-01",
        "file_metadata": {
          "filename": "Movie A",
          "extension": "mkv",
          "absolute_path": "/library/Movie A.mkv",
          "relative_path": "Movie A.mkv",
        }
      }
    })

    try:
      worker = self.build_worker(saved_data_path)
      saved_assets = worker.write_scraped_data("movies", [{
        "title": "Movie A",
        "info_retrieved": "2026-04-09",
        "rating": "8.1",
        "file_metadata": {
          "filename": "Movie A",
          "extension": "mp4",
          "absolute_path": "/library/Movie A.mp4",
          "relative_path": "Movie A.mp4",
        }
      }])
    finally:
      os.unlink(saved_data_path)

    self.assertEqual("keep me", saved_assets["Movie A"]["custom_note"])
    self.assertEqual("2026-04-09", saved_assets["Movie A"]["info_retrieved"])
    self.assertEqual("8.1", saved_assets["Movie A"]["rating"])
    self.assertEqual("mp4", saved_assets["Movie A"]["file_metadata"]["extension"])
