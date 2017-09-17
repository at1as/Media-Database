#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from helpers import get_config_file, HEADERS
import lxml.html
import requests
from scrapers.imdb import *
import time


def get_movie_details(movie, mediatype, movie_url):
  # Scrape movie page for attributes specified below

  if movie_url != None:
    movie_page = lxml.html.document_fromstring(requests.get(movie_url, headers=HEADERS).content)

    return {
      'url':                movie_url,
      'filename':           movie['name'],
      'extension':          movie['extension'],
      'info_retrieved':     time.strftime("%Y-%m-%d"),
      'title':              get_title(movie_page),
      'alternative_title':  get_alternative_title(movie_page),
      'year':               get_movie_year(movie_page),
      'description':        get_description(movie_page),
      'director':           get_director(movie_page),
      'stars':              get_stars(movie_page),
      'genre':              get_genres(movie_page),
      'rating':             get_rating(movie_page),
      'votes':              get_votes(movie_page),
      'running_time':       get_running_time(movie_page),
      'languages':          get_languages(movie_page),
      'content_rating':     get_content_rating(movie_page),
      'awards':             get_awards(movie_page),
      'image_url':          get_image_url(movie_page),
    }


def get_series_details(series, mediatype, series_url):
  # Scrape series page for attributes specified below

  if series_url != None:
    series_page = lxml.html.document_fromstring(requests.get(series_url, headers=HEADERS).content)

    return {
      'url':            series_url,
      'filename':       series['name'],
      'extension':      series['extension'],
      'info_retrieved': time.strftime("%Y-%m-%d"),
      'title':          get_title(series_page),
      'year':           get_series_year(series_page),
      'description':    get_description(series_page),
      'creator':        get_creator(series_page),
      'stars':          get_stars(series_page),
      'genre':          get_genres(series_page),
      'rating':         get_rating(series_page),
      'votes':          get_votes(series_page),
      'running_time':   get_running_time(series_page),
      'languages':      get_languages(series_page),
      'content_rating': get_content_rating(series_page),
      'image_url':      get_image_url(series_page),
    }

