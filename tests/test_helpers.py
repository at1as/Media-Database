from src import helpers
import unittest

class TestHelpers(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_path_of_depth(self):
    self.assertEqual("f/g", helpers.path_of_depth("a/b/c/d/e/f/g", 2))
    self.assertEqual("a/b/c", helpers.path_of_depth("a/b/c", 100))

  def test_verify_config_file(self):
    try:
      helpers.verify_config_file()
    except SystemExit as e:
      self.fail("Exception raised verifying config file: {}".format(e))

  def test_get_config_file(self):
    try:
      helpers.get_config_file()
    except ValueError as e:
      self.fail("Exception thrown reading config file. It is likely not valid JSON")
    except IOError as e:
      self.fail("Exception thrown reading config file. It likely does not exist or has invalid file permissions")

  def test_natural_sort(self):
    episodes = ["season 10", "season 8", "season 1", "season 02"]
    self.assertEqual(
      helpers.natural_sort(episodes),
      ["season 1", "season 02", "season 8", "season 10"]
    )
