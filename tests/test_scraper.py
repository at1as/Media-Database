from src.scraper import Scraper
import unittest

class TestScraper(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass

  def test_scraper_imdb(self):
    scraper = Scraper("IMDB")
    self.assertEqual("<class 'src.scrapers.imdb.IMDB'>", str(scraper.__class__))
  
  @unittest.skip("TMDB api client not yet implemented")
  def test_scraper_tmdb(self):
    scraper = Scraper("TMDB")
    self.assertEqual("<class 'src.scrapers.tmdb.TMDB'>", str(scraper.__class__))
  
  def test_scraper_defaults_to_imdb(self):
    scraper = Scraper("SCRAPER_DOES_NOT_EXIST")
    self.assertEqual("<class 'src.scrapers.imdb.IMDB'>", str(scraper.__class__))
