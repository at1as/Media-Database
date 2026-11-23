import json
import os
import runpy
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import unquote

from lxml import html


ROOT = Path(__file__).resolve().parent.parent
INDEX_PAGES = {"movies": "index.html", "series": "series.html", "standup": "standup.html"}


class TestCatalogWorkflows(unittest.TestCase):

  def setUp(self):
    workspace = tempfile.TemporaryDirectory()
    self.addCleanup(workspace.cleanup)
    self.workspace = Path(workspace.name).resolve()
    self.output = self.workspace / "_output"
    (self.workspace / "_data").mkdir()
    (self.workspace / "_templates").symlink_to(ROOT / "_templates", target_is_directory=True)

    self.config = json.loads((ROOT / "conf.json.template").read_text())
    self.libraries = {}
    for category, settings in self.config["assets"].items():
      library = self.workspace / category
      library.mkdir()
      self.libraries[category] = library
      settings["location"] = str(library) + "/"

    config_file = self.workspace / "conf.json"
    config_file.write_text(json.dumps(self.config))
    original_directory = Path.cwd()
    os.chdir(self.workspace)
    self.addCleanup(os.chdir, original_directory)

    config_path = patch("src.helpers.relative_path", return_value=str(config_file))
    config_path.start()
    self.addCleanup(config_path.stop)

    scraper = patch("src.worker.scraper.Scraper")
    self.scraper = scraper.start()
    self.addCleanup(scraper.stop)
    self.client = self.scraper.return_value
    self.client.get_movie_details.side_effect = self.video_details
    self.client.get_standup_details.side_effect = self.video_details
    self.client.get_series_details.side_effect = self.series_details

    poster = patch("src.worker.Image.save_remote_image")
    self.poster = poster.start()
    self.addCleanup(poster.stop)

    track = SimpleNamespace(
      track_type="Video", format="AVC", width=1920, height=1080, bit_depth=8, bit_rate=1000000
    )
    media_probe = patch("src.helpers.MediaInfo.parse", return_value=SimpleNamespace(tracks=[track]))
    self.media_probe = media_probe.start()
    self.addCleanup(media_probe.stop)

  def run_cli(self, *args):
    script = str(ROOT / "run.py")
    with patch.object(sys, "argv", [script, *args]), redirect_stdout(StringIO()) as output:
      runpy.run_path(script, run_name="__main__")
    return output.getvalue()

  def add_media(self, category, name):
    if category == "series":
      season = self.libraries[category] / name / "Season 2"
      season.mkdir(parents=True)
      path = season / f"{name.removesuffix(' (2024)')} S02E01.mp4"
    else:
      path = self.libraries[category] / f"{name}.mp4"
    path.write_bytes(b"fixture")
    return path

  def catalog_path(self, category):
    return self.workspace / self.config["assets"][category]["saved_data"]

  def read_catalog(self, category):
    return json.loads(self.catalog_path(category).read_text())

  def metadata(self, title, year):
    return {
      "title": title, "year": year, "description": "A test synopsis.",
      "rating": 8.1, "votes": 12345, "genre": ["Drama"], "languages": ["English"],
      "stars": ["Example Actor"], "image_url": "https://example.test/poster.jpg",
      "url": "http://imdb.com/title/tt1230001/?ref_=saved",
    }

  def video_details(self, file_details, _):
    return self.metadata(file_details["name"].removesuffix(" (2024)"), 2024)

  def series_details(self, file_details, _):
    return {
      **self.metadata(file_details["name"].removesuffix(" (2024)"), "2024-2025"),
      "creator": ["Example Creator"],
    }

  def test_count_limits_each_category_and_reruns_do_not_duplicate_records(self):
    expected = {}
    for category in self.libraries:
      names = [f"{category.title()} {letter} (2024)" for letter in ("A", "B")]
      expected[category] = set(names)
      for name in names:
        self.add_media(category, name)

    self.run_cli("--count", "1")
    self.assertEqual(self.scraper.call_count, 3)
    first_batch = {category: self.read_catalog(category) for category in expected}
    for category, records in first_batch.items():
      with self.subTest(category=category):
        self.assertEqual(len(records), 1)
        self.assertTrue(records.keys() <= expected[category])

    self.run_cli("--count", "1")
    self.assertEqual(self.scraper.call_count, 6)
    for category, names in expected.items():
      with self.subTest(category=category):
        saved = self.read_catalog(category)
        self.assertEqual(saved.keys(), names)
        for name, record in first_batch[category].items():
          self.assertEqual(saved[name], record)

    before = {category: self.catalog_path(category).read_bytes() for category in expected}
    self.run_cli("--count", "1")
    self.assertEqual(self.scraper.call_count, 6)
    for category, payload in before.items():
      with self.subTest(category=category):
        self.assertEqual(self.catalog_path(category).read_bytes(), payload)

  def test_failed_lookup_uses_one_attempt_and_preserves_the_saved_movie(self):
    self.add_media("movies", "Saved Feature (2024)")
    self.run_cli("--count", "1")
    catalog = self.catalog_path("movies")
    before = catalog.read_bytes()
    self.add_media("movies", "Pending Feature A (2024)")
    self.add_media("movies", "Pending Feature B (2024)")
    self.client.get_movie_details.reset_mock()
    self.client.get_movie_details.side_effect = OSError("IMDb timed out")

    output = self.run_cli("--count", "1")

    self.client.get_movie_details.assert_called_once()
    self.assertIn("IMDb timed out", output)
    self.assertEqual(catalog.read_bytes(), before)
    self.assertTrue((self.output / "movies" / "Saved Feature(2024).html").is_file())

  def test_dry_run_renders_saved_catalog_and_resolves_detail_links(self):
    names = {
      "movies": "Feature: After Dark",
      "series": "Harbor Signal",
      "standup": "A Night of Jokes",
    }
    video_paths = {}
    before = {}
    for category, title in names.items():
      name = f"{title} (2024)"
      media_path = self.add_media(category, name)
      if category == "series":
        details = {
          "directory": {"name": name},
          "creator": ["Example Creator"],
          "episodes": [{media_path.stem: {"resolution": "1080p"}}],
        }
      else:
        video_paths[category] = media_path
        details = {
          "file_metadata": {"filename": name, "extension": "mp4", "absolute_path": str(media_path)},
          "media": {"resolution": "1080p"},
        }
      if category == "movies":
        details["trailer_url"] = "http://m.imdb.com/video/vi1234567?ref_=saved"

      year = "2024-2025" if category == "series" else 2024
      records = {name: {**self.metadata(title, year), **details}}
      if category == "movies":
        records["Incomplete title"] = {"title": "Incomplete title", "year": 2024}
      catalog = self.catalog_path(category)
      catalog.write_text(json.dumps(records))
      before[category] = catalog.read_bytes()

    self.run_cli("--dry-run")

    self.scraper.assert_not_called()
    self.poster.assert_not_called()
    self.media_probe.assert_not_called()
    self.assertTrue((self.output / "about.html").is_file())
    for category, title in names.items():
      with self.subTest(category=category):
        self.assertEqual(self.catalog_path(category).read_bytes(), before[category])
        index = html.parse(str(self.output / INDEX_PAGES[category]))
        links = index.xpath("//a[@data-title-details]")
        title_links = index.xpath("//a[@data-title-details and normalize-space(.)]")
        self.assertEqual([link.text_content().strip() for link in title_links], [title])

        detail_path = self.output / unquote(title_links[0].get("href"))
        self.assertEqual(detail_path.parent, self.output / category)
        self.assertEqual({self.output / unquote(link.get("href")) for link in links}, {detail_path})
        detail = html.parse(str(detail_path))
        self.assertIn("https://www.imdb.com/title/tt1230001/", detail.xpath("//a/@href"))
        trailers = detail.xpath("//a[contains(@class, 'trailer-button')]/@href")
        self.assertEqual(trailers, ["https://www.imdb.com/video/vi1234567/"] if category == "movies" else [])
        if category == "series":
          self.assertIn("Season 2", detail.xpath("normalize-space(//summary[@class='season-header'])"))
          self.assertEqual(detail.xpath("//span[@class='episode-name']/text()"), ["Harbor Signal S02E01"])
          self.assertEqual(detail.xpath("//span[contains(@class, 'episode-resolution')]/text()"), ["1080p"])
        else:
          self.assertEqual(detail.xpath("//video/@src"), [str(video_paths[category])])
