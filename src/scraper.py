#!/usr/bin/env python
# -*- coding: utf8 -*-


from .helpers import HEADERS
from .scrapers.imdbv1 import IMDBV1
from .scrapers.imdbv2 import IMDBV2
from .scrapers.imdb_suggest import IMDB_SUGGEST

class Scraper(object):

  # IMDB - http://www.imdb.com
  # TMDB - https://www.themoviedb.org
  sources = ("IMDBV1", "IMDBV2", "IMDB_SUGGEST", "IMDB_API", "TMDB",)

  def __new__(cls, source, *args, **kwargs):
    """
      If no supported scraper is set, use IMDBV2 scraper by default
    """

    if source not in Scraper.sources:
      return IMDBV2(*args, **kwargs)

    elif source == "IMDBV1":
      # Deprecated, in house scraper
      return IMDBV1(*args, **kwargs)

    elif source == "IMDBV2":
      # Preferred scraper for IMDB, maintined using cinemagoer dependency
      return IMDBV2(*args, **kwargs)

    elif source == "IMDB_SUGGEST" or source == "IMDB_API":
      # Alternative IMDb scraper using Suggestions API for ID resolution
      print("DEBUG: Scraper factory creating IMDB_SUGGEST instance for source='{}'".format(source))
      return IMDB_SUGGEST(*args, **kwargs)

    elif source == "TMDB":
      # TODO
      raise NotImplementedError("TMDB scraper not implemented yet")

    elif source == "RottenTomatoes":
      # TODO
      raise NotImplementedError("RottenTomatoes scraper not implemented yet")
