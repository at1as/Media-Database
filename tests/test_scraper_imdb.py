#-*- encoding:utf8 -*-

import codecs
import lxml
from src.scraper import Scraper
import unittest


import sys
import imp
imp.reload(sys)
sys.setdefaultencoding('utf8')


class TestScraper(unittest.TestCase):
  
  def setUp(self):
    self.scraper = Scraper("IMDB")
    
    with codecs.open("./tests/fixtures/imdb_fight_club_movie_page_2018_09_10_minified.html") as f:
      self.movie_page_str = f.read().replace('\n', '')
      self.movie_page_xml = lxml.html.document_fromstring(self.movie_page_str)
  
  def tearDown(self):
    pass

  def test_construct_search_url(self):
    search_url = self.scraper.construct_search_url("Fight Club (1999)")
    self.assertEqual("http://www.imdb.com/find?q=fight+club+(1999)&s=all", search_url)
  
  def test_construct_search_url_unicode(self):
    search_url = self.scraper.construct_search_url("Amélie (2001)")
    self.assertEqual("http://www.imdb.com/find?q=am\xe9lie+(2001)&s=all", search_url)

  def test_get_title(self):
    self.assertEqual("Fight Club", self.scraper.get_title(self.movie_page_xml))
  
  def test_get_title(self):
    self.assertEqual([], self.scraper.get_alternative_title(self.movie_page_xml))

  def test_get_description(self):
    self.assertEqual(
      'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.',
      self.scraper.get_description(self.movie_page_xml)
    )

  def test_get_director(self):
    self.assertEqual(['David Fincher'], self.scraper.get_director(self.movie_page_xml))

  def test_rating(self):
    self.assertEqual("8.8", self.scraper.get_rating(self.movie_page_xml))

  def test_get_genres(self):
    self.assertEqual(['Drama'], self.scraper.get_genres(self.movie_page_xml))

  def test_get_votes(self):
    self.assertEqual("1,595,752", self.scraper.get_votes(self.movie_page_xml))

  def test_get_running_time(self):
    self.assertEqual("2h 19min", self.scraper.get_running_time(self.movie_page_xml))

  def test_get_content_rating(self):
    self.assertEqual('R', self.scraper.get_content_rating(self.movie_page_xml))

  def test_get_stars(self):
    self.assertEqual(
      ['Brad Pitt', 'Edward Norton', 'Meat Loaf'],
      self.scraper.get_stars(self.movie_page_xml)
    )

  def test_get_languages(self):
    self.assertEqual(['English'], self.scraper.get_languages(self.movie_page_xml))

  def test_get_image_url(self):
    self.assertEqual(
        'https://m.media-amazon.com/images/M/MV5BMjJmYTNkNmItYjYyZC00MGUxLWJhNWMtZDY4Nzc1MDAwMzU5XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UX182_CR0,0,182,268_AL_.jpg',
      self.scraper.get_image_url(self.movie_page_xml)
    )

  def test_get_movie_year(self):
    self.assertEqual('1999', self.scraper.get_movie_year(self.movie_page_xml))

  def test_get_awards(self):
    self.assertEqual('Nominated for 1 Oscar.', self.scraper.get_awards(self.movie_page_xml))
