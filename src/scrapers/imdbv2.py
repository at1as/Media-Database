#!/usr/bin/env python
# -*- coding: utf8 -*-


from ..helpers import HEADERS, verify_config_file
import time
from unicodedata import normalize
from imdb import Cinemagoer
import re

class IMDBV2(object):
  BASE_URL = "https://www.imdb.com"
  MOVIE_PATH = "/title/tt"
  SKIP_LIST_PATH = "./skip_list"

  def __init__(self, title, foreign_id=None):
    self.scraper = Cinemagoer()
    self.config = verify_config_file()

    print("Scraping IMDB for: '{}'".format(title))

    if foreign_id is not None:
      movie_id = foreign_id
    else:
      safe_title = normalize("NFC", str(title))

      base_title, year = self.__split_title_year(safe_title)

      # First try a standard search on the full safe title
      self.hits = self.scraper.search_movie(safe_title)

      # If no hits, try without year, then try advanced (with year) if available
      if len(self.hits) == 0 and base_title != safe_title:
        self.hits = self.scraper.search_movie(base_title)

      if len(self.hits) == 0 and year is not None:
        try:
          self.hits = self.scraper.search_movie_advanced(base_title, results=None, year=year)
        except Exception:
          pass

      # If still no hits, try stripping subtitles after colon or dash
      if len(self.hits) == 0:
        stripped = re.split(r"[:\-]", base_title)[0].strip()
        if stripped and stripped != base_title:
          self.hits = self.scraper.search_movie(stripped)

      if len(self.hits) == 0:
        self.__add_to_skip_list(safe_title)
        raise Exception("No results found for {}. Skipping".format(safe_title))

      self.__sleep()

      # Choose the best matching hit by title/year
      best = self.__select_best_hit(self.hits, base_title, year)
      movie_id = best.movieID

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
      skip_list.write(title + "\n")

  def __clean(self, s: str) -> str:
    s = s.lower()
    s = re.sub(r"\(\d{4}\)$", "", s).strip()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

  def __split_title_year(self, s: str):
    m = re.search(r"\((\d{4})\)\s*$", s)
    if m:
      try:
        return s[:m.start()].strip(), int(m.group(1))
      except Exception:
        return s, None
    return s, None

  def __select_best_hit(self, hits, base_title: str, year: int | None):
    base_clean = self.__clean(base_title)
    best = None
    # Prefer exact cleaned title match and matching year
    for h in hits:
      try:
        t = self.__clean(h.get('title', '') or '')
        y = h.get('year', None)
        if t == base_clean and (year is None or y == year):
          return h
        if best is None:
          best = h
      except Exception:
        continue
    # Prefer matching year if available
    if year is not None:
      for h in hits:
        try:
          if h.get('year', None) == year:
            return h
        except Exception:
          continue
    return best or hits[0]

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

  def get_standup_details(self, standup, standup_url):
    """ Scrape standup page for attributes specified below """
    return self.get_movie_details(standup, standup_url)
