#!/usr/bin/env python
# -*- coding: utf8 -*-


from ..helpers import HEADERS, verify_config_file
import time
from unicodedata import normalize
from imdb import Cinemagoer

class IMDBV2(object):
  BASE_URL = "http://www.imdb.com"
  MOVIE_PATH = "/title/tt"
  SKIP_LIST_PATH = "./skip_list"

  def __init__(self, title, foreign_id=None):
    self.scraper = Cinemagoer()
    self.config = verify_config_file()

    print(("Scraping IMDB for: '{}'".format(title).encode('utf-8')))

    if foreign_id is not None:
      movie_id = foreign_id
    else:
      self.hits = self.scraper.search_movie("{}".format(title).encode('utf-8'))
      if len(self.hits) == 0:
        self.__add_to_skip_list(title)
        raise Exception("No results found for {}. Skipping".format(title))
      self.__sleep()
      movie_id = self.hits[0].movieID

    print(("Searching for movie with id: {}".format(movie_id)))

    self.detailed_hit = self.scraper.get_movie(movie_id)
    self.__sleep()

  def __sleep(self):
    sleep_time = self.config.get("pause_time_sec", 1)
    print("Sleeping for {} seconds".format(sleep_time))
    time.sleep(sleep_time)

  def __assemble_url(self, movie_id):
    return self.BASE_URL + self.MOVIE_PATH + movie_id

  def __add_to_skip_list(self, title):
    with open(self.SKIP_LIST_PATH, "a") as skip_list:
      skip_list.write(title)

  def __extract_first(self, list):
    return list[0] if list is not None and len(list) > 0 else ''

  def get_movie_details(self, movie_name, movie_url):
    """ Scrape movie page for attributes specified below """

    return {
        'url':                self.__assemble_url(self.detailed_hit['imdbID']),
        'info_retrieved':     time.strftime("%Y-%m-%d"),
        'title':              self.detailed_hit.get('title'),
        'alternative_title':  self.detailed_hit.get('original title'),
        'year':               self.detailed_hit.get('year'),
        'description':        self.__extract_first(self.detailed_hit.get('plot')),
        'director':           [director.get('name') for director in self.detailed_hit.get('director', [])],
        'stars':              [cast.get('name') for cast in self.detailed_hit.get('cast', [])],
        'genre':              self.detailed_hit.get('genres'),
        'rating':             self.detailed_hit.get('rating'),
        'votes':              self.detailed_hit.get('votes'),
        'running_time':       self.__extract_first(self.detailed_hit.get('runtimes')),
        'languages':          self.detailed_hit.get('languages'),
        'content_rating':     self.__extract_first([certification.split(":")[1] for certification in self.detailed_hit.get('certificates', []) if certification.startswith("United States")]),
        'awards':             "", # TODO: .get_movie('0133093', info=['awards'])
        'image_url':          self.detailed_hit.get('full-size cover url'),
        'type':               self.detailed_hit.get('kind'),
    }

  def get_series_details(self, series, series_url):
    """ Scrape series page for attributes specified below """

    return {
        'url':               self.__assemble_url(self.detailed_hit['imdbID']),
        'info_retrieved':    time.strftime("%Y-%m-%d"),
        'title':             self.detailed_hit.get('title'),
        'alternative_title': self.detailed_hit.get('akas'),
        'year':              self.detailed_hit.get('series years'),
        'description':       self.__extract_first(self.detailed_hit.get('plot')),
        'creator':           [creator.get('name') for creator in self.detailed_hit.get('creator', [])],
        'stars':             [cast.get('name') for cast in self.detailed_hit.get('cast', [])],
        'genre':             self.detailed_hit.get('genres'),
        'rating':            self.detailed_hit.get('rating'),
        'votes':             self.detailed_hit.get('votes'),
        'running_time':      self.__extract_first(self.detailed_hit.get('runtimes')),
        'languages':         self.detailed_hit.get('languages'),
        'content_rating':    self.__extract_first([certificaton.split(":")[1] for certificaton in self.detailed_hit.get('certificates', []) if certificaton.startswith("United States")]),
        'image_url':         self.detailed_hit.get('full-size cover url'),
        'type':              self.detailed_hit.get('kind'),
    }
