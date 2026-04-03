#!/usr/bin/env python
# -*- coding: utf8 -*-


from .helpers import HEADERS
from .scrapers.imdbv1 import IMDBV1
from .scrapers.imdb_suggest import IMDB_SUGGEST

class Scraper(object):

  # IMDB - http://www.imdb.com
  # TMDB - https://www.themoviedb.org
  sources = ("IMDBV1", "IMDBV2", "IMDB_SUGGEST", "IMDB_API", "TMDB",)

  def __new__(cls, source, *args, **kwargs):
    """
      If no supported scraper is set, use IMDB_SUGGEST scraper by default
    """

    if source not in Scraper.sources:
      return IMDB_SUGGEST(*args, **kwargs)

    elif source == "IMDBV1":
      # Deprecated, in house scraper
      return IMDBV1(*args, **kwargs)

    elif source == "IMDBV2":
      # Legacy alias retained for config compatibility
      print("DEBUG: Scraper factory remapping legacy source='IMDBV2' to IMDB_SUGGEST")
      return IMDB_SUGGEST(*args, **kwargs)

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
