import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src import helpers

class TestHelpers(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_path_of_depth(self):
    self.assertEqual("f/g", helpers.path_of_depth("a/b/c/d/e/f/g", 2))
    self.assertEqual("a/b/c", helpers.path_of_depth("a/b/c", 100))

  def test_verify_config_file(self):
    template = Path(__file__).resolve().parent.parent / "conf.json.template"
    with patch("src.helpers.relative_path", return_value=template):
      self.assertEqual(helpers.verify_config_file(), json.loads(template.read_text()))

  def test_get_config_file(self):
    config = {"include_extensions": ["mp4"]}
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "conf.json"
      path.write_text(json.dumps(config))
      with patch("src.helpers.relative_path", return_value=path):
        self.assertEqual(helpers.get_config_file(), config)

  def test_natural_sort(self):
    episodes = ["season 10", "season 8", "season 1", "season 02"]
    self.assertEqual(
      helpers.natural_sort(episodes),
      ["season 1", "season 02", "season 8", "season 10"]
    )


  def test_video_media_details_retries_with_binary_stream(self):
    video = SimpleNamespace(
      track_type="Video", format="HEVC", width=1920, height=1080, bit_depth=10, bit_rate=2000000
    )
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "Title꞉ Subtitle.mkv"
      path.write_bytes(b"example media")

      def parse(source):
        if source == str(path):
          raise RuntimeError("MediaInfo could not open the path")
        self.assertEqual(source.read(), b"example media")
        return SimpleNamespace(tracks=[video])

      with patch("src.helpers.MediaInfo.parse", side_effect=parse) as media_parse:
        details = helpers.video_media_details(str(path))

    self.assertEqual(media_parse.call_count, 2)
    self.assertEqual(details["format"], "HEVC")
    self.assertEqual(details["resolution"], "1080p")
