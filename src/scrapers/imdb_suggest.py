#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import time
import urllib.parse
from unicodedata import normalize

import requests
from imdbinfo import get_movie as imdbinfo_get_movie

from ..helpers import HEADERS, verify_config_file


class IMDB_SUGGEST(object):
  BASE_URL = "https://www.imdb.com"
  SUGGEST_V3 = "https://v3.sg.media-imdb.com/suggestion"
  SUGGEST_V2 = "https://v2.sg.media-imdb.com/suggestion"

  def __init__(self, title: str, foreign_id: str | None = None):
    print("DEBUG: IMDB_SUGGEST.__init__ called with title='{}', foreign_id='{}'".format(title, foreign_id))
    self.config = verify_config_file()
    self.imdb_id = None
    self.numeric_id = None
    print("DEBUG: Initialized imdb_id={}, numeric_id={}".format(self.imdb_id, self.numeric_id))

    print("Scraping IMDB (Suggestions) for: '{}'".format(title))

    if foreign_id is not None:
      self.imdb_id = foreign_id if str(foreign_id).startswith("tt") else "tt{}".format(foreign_id)
    else:
      safe_title = normalize("NFC", str(title))
      base_title, year = self.__split_title_year(safe_title)

      suggestions = self.__fetch_suggestions(safe_title) or []
      if not suggestions and base_title != safe_title:
        suggestions = self.__fetch_suggestions(base_title) or []

      if not suggestions:
        stripped = re.split(r"[:\-]", base_title)[0].strip()
        if stripped and stripped != base_title:
          suggestions = self.__fetch_suggestions(stripped) or []

      if not suggestions:
        raise Exception("No results found for {} via Suggestions API. Skipping".format(safe_title))

      best = self.__select_best_suggestion(suggestions, base_title, year)
      if best is None:
        raise Exception("No suitable suggestion found for {}".format(safe_title))

      self.imdb_id = best.get('id')
      if not self.imdb_id:
        raise Exception("No IMDb ID found for {} via Suggestions API".format(safe_title))

    if isinstance(self.imdb_id, str):
      self.numeric_id = self.imdb_id.replace('tt', '')

  def __sleep(self):
    sleep_time = self.config.get("pause_time_sec", 1)
    print("Sleeping for {} seconds".format(sleep_time))
    time.sleep(sleep_time)

  def __split_title_year(self, title: str):
    match = re.search(r"\((\d{4})\)\s*$", title)
    if match:
      try:
        return title[:match.start()].strip(), int(match.group(1))
      except Exception:
        return title, None
    return title, None

  def __clean(self, title: str) -> str:
    title = title.lower()
    title = re.sub(r"\(\d{4}\)$", "", title).strip()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title

  def __fetch_suggestions(self, query: str):
    query = query.strip()
    if not query:
      return None

    first = self.__clean(query)[:1] or '0'
    encoded = urllib.parse.quote(query)
    headers = {
      **HEADERS,
      'accept': 'application/json, text/plain, */*',
      'accept-language': 'en-US,en;q=0.9',
      'origin': 'https://m.imdb.com',
      'priority': 'u=1, i',
      'referer': 'https://m.imdb.com/',
      'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
    }
    params = {'includeVideos': '1'}

    for base_url in [self.SUGGEST_V3, self.SUGGEST_V2]:
      try:
        url = "{}/{}/{}.json".format(base_url, first, encoded)
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
          return response.json().get('d', [])
      except Exception:
        continue

    return None

  def __select_best_suggestion(self, items, base_title: str, year: int | None):
    base_clean = self.__clean(base_title)
    best = None
    acceptable_qid = {"movie", "tvSeries", "tvMiniSeries", "video"}
    excluded_qid = {"short", "videoGame", "podcastEpisode"}

    def is_acceptable_title(item):
      item_id = item.get('id') or ''
      if not item_id.startswith('tt'):
        return False
      qid = item.get('qid')
      if qid in excluded_qid:
        return False
      return (qid in acceptable_qid) or (qid is None)

    filtered = [item for item in items if is_acceptable_title(item)] or [
      item for item in items if (item.get('id') or '').startswith('tt')
    ]

    for item in filtered:
      try:
        suggestion_title = self.__clean(item.get('l', '') or '')
        suggestion_year = item.get('y')
        if suggestion_title == base_clean and (year is None or suggestion_year == year):
          return item
        if best is None:
          best = item
      except Exception:
        continue

    if year is not None:
      for item in filtered:
        try:
          if item.get('y') == year:
            return item
        except Exception:
          continue

    return best or (filtered[0] if filtered else (items[0] if items else None))

  def __assemble_url(self, imdb_id: str):
    return "{}/title/{}".format(self.BASE_URL, imdb_id)

  def __extract_names(self, people):
    names = []
    if not isinstance(people, list):
      return names

    for person in people:
      if isinstance(person, dict):
        name = person.get('name')
      else:
        name = getattr(person, 'name', None)

      if name and name not in names:
        names.append(name)

    return names

  def __cast_names_from_imdbinfo(self, data: dict):
    categories = data.get('categories') or {}
    cast_names = self.__extract_names(categories.get('cast'))
    if cast_names:
      return cast_names
    return self.__extract_names(data.get('stars'))

  def __unique_values(self, values):
    result = []
    for value in values:
      if value in [None, ""]:
        continue
      if value not in result:
        result.append(value)
    return result

  def __preferred_title_fields(self, data: dict, mediatype: str):
    base_title = data.get('title')
    localized_title = data.get('title_localized')
    akas = list(data.get('title_akas') or [])

    preferred_title = localized_title or base_title

    if mediatype == 'series':
      alternative_title = self.__unique_values(([base_title] if preferred_title != base_title else []) + akas)
    else:
      alternatives = self.__unique_values(([base_title] if preferred_title != base_title else []) + akas)
      alternative_title = alternatives[0] if alternatives else None

    return preferred_title, alternative_title

  def __content_rating_from_imdbinfo(self, data: dict):
    certificates = data.get('certificates') or {}
    if isinstance(certificates, dict):
      for country_key in ['US', 'United States', 'USA']:
        rating = certificates.get(country_key)
        if isinstance(rating, str) and rating:
          return self.__normalize_certificate_value(rating)
        if isinstance(rating, list) and rating:
          return self.__normalize_certificate_value(rating[0])
        if isinstance(rating, tuple) and len(rating) >= 2 and rating[1]:
          return self.__normalize_certificate_value(rating[1])

    content_rating = data.get('mpaa')
    if content_rating:
      return self.__normalize_certificate_value(content_rating)

    return None

  def __normalize_certificate_value(self, value):
    value = str(value).strip()
    if not value:
      return None

    value = re.sub(r"\s+certificate.*$", "", value, flags=re.IGNORECASE).strip()
    value = re.sub(r"\s+cert#.*$", "", value, flags=re.IGNORECASE).strip()
    value = re.sub(r"\s+self[- ]applied.*$", "", value, flags=re.IGNORECASE).strip()
    return value

  def __running_time_from_imdbinfo(self, data: dict):
    duration = data.get('duration')
    if duration in [None, ""]:
      return None

    try:
      duration = int(duration)
      if duration <= 0:
        return None

      # imdbinfo is currently returning duration in minutes for title details.
      # Keep a defensive fallback for any unusually large second-based values.
      if duration > 400:
        return int(duration / 60)

      return duration
    except Exception:
      return duration

  def __fetch_details_from_imdbinfo(self, mediatype: str):
    imdb_id = self.imdb_id if str(self.imdb_id).startswith('tt') else "tt{}".format(self.imdb_id)
    print("DEBUG: Fetching '{}' details from imdbinfo for IMDb id '{}'".format(mediatype, imdb_id))

    detail = imdbinfo_get_movie(imdb_id)
    if detail is None:
      raise Exception("imdbinfo returned no details for {}".format(imdb_id))

    data = detail.model_dump() if hasattr(detail, 'model_dump') else detail
    info_series = data.get('info_series') or {}

    creators = self.__extract_names(info_series.get('creators'))
    directors = self.__extract_names(data.get('directors'))
    stars = self.__cast_names_from_imdbinfo(data)
    languages = data.get('languages_text') or data.get('languages')
    year = data.get('year')
    preferred_title, alternative_title = self.__preferred_title_fields(data, mediatype)

    if mediatype == 'series' and year not in [None, ""]:
      year = str(year)

    payload = {
      'url': data.get('url') or self.__assemble_url(imdb_id),
      'info_retrieved': time.strftime("%Y-%m-%d"),
      'title': preferred_title,
      'alternative_title': alternative_title,
      'year': year,
      'description': data.get('plot'),
      'director': directors,
      'creator': creators,
      'stars': stars,
      'genre': data.get('genres'),
      'rating': data.get('rating'),
      'votes': data.get('votes'),
      'running_time': self.__running_time_from_imdbinfo(data),
      'languages': languages,
      'content_rating': self.__content_rating_from_imdbinfo(data),
      'awards': "",
      'image_url': data.get('cover_url'),
      'trailer_url': (data.get('trailers') or [None])[0],
      'type': 'tvSeries' if mediatype == 'series' else 'movie',
    }

    if mediatype == 'series' and not payload['creator'] and directors:
      payload['creator'] = directors

    return payload

  def get_movie_details(self, movie, movie_url):
    if not self.imdb_id:
      raise Exception("No IMDb id available for movie")
    self.__sleep()
    return self.__fetch_details_from_imdbinfo('movie')

  def get_series_details(self, series, series_url):
    if not self.imdb_id:
      raise Exception("No IMDb id available for series")
    self.__sleep()
    return self.__fetch_details_from_imdbinfo('series')

  def get_standup_details(self, standup, standup_url):
    return self.get_movie_details(standup, standup_url)
