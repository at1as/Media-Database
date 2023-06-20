#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from helpers import HEADERS
from scrapers.imdbv1 import IMDBV1
from scrapers.imdbv2 import IMDBV2

class Scraper(object):

  # IMDB - http://www.imdb.com
  # TMDB - https://www.themoviedb.org
  sources = ("IMDBV1", "IMDBV2", "TMDB",)

  def __new__(cls, source, *args, **kwargs):
    """
      If no supported scraper is set, use IMDBV2 scraper by default
    """

    if source not in Scraper.sources:
      return super(Scraper, cls).__new__(IMDBV2, *args, **kwargs)

    elif source == "IMDBV1":
      # Deprecated, in house scraper
      return super(Scraper, cls).__new__(IMDBV1, *args, **kwargs)

    elif source == "IMDBV2":
      # Preferred scraper for IMDB, maintined using cinemagoer dependency
      return super(Scraper, cls).__new__(IMDBV2, *args, **kwargs)

    elif source == "TMDB":
      # TODO
      raise NotImplementedError("TMDB scraper not implemented yet")

    elif source == "RottenTomatoes":
      # TODO
      raise NotImplementedError("RottenTomatoes scraper not implemented yet")
