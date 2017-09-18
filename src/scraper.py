#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from helpers import get_config_file, HEADERS
import lxml.html
import requests
from scrapers.imdb import IMDB
import time


class Scraper(object):
  
  sources = ("IMDB",)

  def __new__(cls, source, *args, **kwargs):
    """
      currently the only supported scraper is IMDB, but more will be added
      if no supported scraper is set, use IMDB by default
    """

    if source not in Scraper.sources:
      return super(Scraper, cls).__new__(IMDB(), *args, **kwargs)
    elif source == "IMDB":
      return super(Scraper, cls).__new__(IMDB, *args, **kwargs)

