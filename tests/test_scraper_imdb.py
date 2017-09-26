#-*- encoding:utf8 -*-
from __future__ import unicode_literals
from src.scraper import Scraper
import unittest

class TestScraper(unittest.TestCase):
  
  def setUp(self):
    self.scraper = Scraper("IMDB")  
  
  def tearDown(self):
    pass

  def test_construct_search_url(self):
    search_url = self.scraper.construct_search_url("Fight Club (1999)")
    self.assertEquals("http://www.imdb.com/find?q=fight+club+(1999)&s=all", search_url)
  
  def test_construct_search_url_unicode(self):
    search_url = self.scraper.construct_search_url(u"Amélie (2001)")
    self.assertEquals("http://www.imdb.com/find?q=am\xe9lie+(2001)&s=all", search_url)
