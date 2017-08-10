#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from helpers import get_config_file, HEADERS
import lxml.html
import requests
import time


def get_movie_details(movie, mediatype, movie_url):
  # Scrape movie page for attributes specified below

  if movie_url != None:
    movie_page = lxml.html.document_fromstring(requests.get(movie_url, headers=HEADERS).content)

    movie_attributes = {
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
    try:    save_image(movie_attributes['image_url'], movie_attributes['filename'], mediatype)
    except: pass

    return movie_attributes
  else:
    return None


def get_series_details(series, mediatype, series_url):
  # Scrape series page for attributes specified below

  if series_url != None:
    series_page = lxml.html.document_fromstring(requests.get(series_url, headers=HEADERS).content)

    series_attributes = {
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
    try:    save_image(series_attributes['image_url'], series_attributes['filename'], mediatype)
    except: pass

    return series_attributes
  else:
    return None


def get_title(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="title_block"]//h1/text()')[0].strip()
  except IndexError:
    return ''

def get_alternative_title(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="title_wrapper"]//div[@class="originalTitle"]/text()')
  except IndexError:
    return ''

def get_description(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="summary_text"]')[0].text_content().strip().replace('See full summary', '')
  except IndexError:
    return ''

def get_director(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="plot_summary_wrapper"]/div[1]/div[2]/span/a/span/text()')
  except IndexError:
    return ''

def get_rating(xml_doc):
  try:
    return xml_doc.xpath('//span[@itemprop="ratingValue"]/text()')[0].strip()
  except IndexError:
    return ''

def get_genres(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="title_wrapper"]//div[@class="subtext"]//span[@itemprop="genre"]/text()')
  except IndexError:
    return ''

def get_votes(xml_doc):
  try:
    return xml_doc.xpath('//span[@itemprop="ratingCount"]/text()')[0].strip()
  except IndexError:
    return ''

def get_running_time(xml_doc):
  try:
    return xml_doc.xpath('//time[@itemprop="duration"]/text()')[0].strip()
  except IndexError:
    return ''

def get_content_rating(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="title_wrapper"]/div[@class="subtext"]//*[@itemprop="contentRating"]/@content')
  except IndexError:
    return ''

def get_stars(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="title-overview"]//*[@itemprop="actors"]/a/span/text()')
  except IndexError:
    try:
      return xml_doc.xpath('//div[@class="plot_summary_wrapper"]/div[1]/div[3]/span/a/span/text()')
    except IndexError:
      return ''

def get_languages(xml_doc):
  try:
    if xml_doc.xpath('//*[@id="titleDetails"]/div[3]/h4/text()') == ['Language:']:
      return xml_doc.xpath('//*[@id="titleDetails"]/div[3]/a/text()')
    else:
      return xml_doc.xpath('//*[@id="titleDetails"]/div[2]/a/text()')
  except IndexError:
    return ''

def get_image_url(xml_doc):
  try:
    return xml_doc.xpath('//*[@class="poster"]/a/img/@src')[0]
  except IndexError:
    return ''

# Movie specific
def get_movie_year(xml_doc):
  try:
    return xml_doc.xpath('//*[@class="title_wrapper"]//span[@id="titleYear"]/a/text()')[0]
  except IndexError:
    return ''

def get_awards(xml_doc):
  try:
    awards = xml_doc.xpath('//*[@id="titleAwardsRanks"]/span[@itemprop="awards"]/b/text()')[0].strip()
    if not "oscar" in awards.lower():
      return ''
    else:
      if awards[-1:] == ".":
        return ' '.join(xml_doc.xpath('//*[@id="titleAwardsRanks"]/span[@itemprop="awards"]/b/text()')[0].strip().split())
      try:
        return get_config_file()['base_url'] + movie_page.xpath('//*[@id="titleAwardsRanks"]/span[@class="see-more inline"]/a/@href')[0]
      except IndexError:
        return ''
  except IndexError:
    return ''

# Series Specific
def get_series_year(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="title_wrapper"]//div[@class="subtext"]/a/text()')[0].strip().split('(')[-1].split(')')[0].strip()
  except IndexError:
    return ''

def get_creator(xml_doc):
  try:
    return xml_doc.xpath('//div[@class="title-overview"]//*[@itemprop="creator"]/a/span/text()')
  except IndexError:
    return ''
