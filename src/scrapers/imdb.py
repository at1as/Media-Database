#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from ..helpers import get_config_file, HEADERS
import lxml.html
import requests
import time
from   unicodedata import normalize


def construct_search_url(title):
  # Construct search results url for specified title

  safe_title = normalize("NFC", title).replace(" ", "+").replace("&", "%26").replace("?", "%3F").lower()
  return get_config_file()["base_url"] + get_config_file()["search_path"] + safe_title + get_config_file()["url_end"]

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
    return xml_doc.xpath('//div[@class="summary_text"]')[0].text_content().strip().replace('See full summary', '').replace('»', '').strip()
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

# Movie specific functions
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

# Series Specific Functions
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
