#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from retriever import *

def get_movie_details(movie, mediatype):
  # Scrape movie page for attributes specified below

  movie_attributes = {}
  movie_url = get_title_url(movie['name'], mediatype)

  if movie_url != None:
    movie_page = lxml.html.document_fromstring(requests.get(movie_url, headers=headers).content)

    movie_attributes['url'] = movie_url
    movie_attributes['filename'] = movie['name']
    movie_attributes['extension'] = movie['extension']
    movie_attributes['info_retrieved'] = time.strftime("%Y-%m-%d")
    movie_attributes['title'] = get_title(movie_page)
    movie_attributes['alternative_title'] = get_alternative_title(movie_page)
    movie_attributes['year'] = get_movie_year(movie_page)
    movie_attributes['description'] = get_description(movie_page)
    movie_attributes['director'] = get_director(movie_page)
    movie_attributes['stars'] = get_stars(movie_page)
    movie_attributes['genre'] = get_genres(movie_page)
    movie_attributes['rating'] = get_rating(movie_page)
    movie_attributes['votes'] = get_votes(movie_page)
    movie_attributes['running_time'] = get_running_time(movie_page)
    movie_attributes['languages'] = get_languages(movie_page)
    movie_attributes['content_rating'] = get_content_rating(movie_page)
    movie_attributes['awards'] = get_awards(movie_page)
    movie_attributes['image_url'] = get_image_url(movie_page)
    try:    save_image(movie_attributes['image_url'], movie_attributes['filename'], mediatype)
    except: pass

    return movie_attributes
  else:
    return None


def get_series_details(series, mediatype):
  # Scrape series page for attributes specified below

  series_attributes = {}
  series_url = get_title_url(series['name'], mediatype)

  if series_url != None:
    series_page = lxml.html.document_fromstring(requests.get(series_url, headers=headers).content)

    series_attributes['url'] = series_url
    series_attributes['filename'] = series['name']
    series_attributes['extension'] = series['extension']
    series_attributes['info_retrieved'] = time.strftime("%Y-%m-%d")
    series_attributes['title'] = get_title(series_page)
    series_attributes['year'] = get_series_year(series_page)
    series_attributes['description'] = get_description(series_page)
    series_attributes['creator'] = get_creator(series_page)
    series_attributes['stars'] = get_stars(series_page)
    series_attributes['genre'] = get_genres(series_page)
    series_attributes['rating'] = get_rating(series_page)
    series_attributes['votes'] = get_votes(series_page)
    series_attributes['running_time'] = get_running_time(series_page)
    series_attributes['languages'] = get_languages(series_page)
    series_attributes['content_rating'] = get_content_rating(series_page)
    series_attributes['image_url'] = get_image_url(series_page)
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
    return xml_doc.xpath('//div[@class="summary_text"]/text()')[0].strip().replace('See full summary', '')
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
    #return xml_doc.xpath('//div[@class="plot_summary_wrapper"]/div[1]/div[4]/span/a/span/text()') ## DELETE ME
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
        return config['base_url'] + movie_page.xpath('//*[@id="titleAwardsRanks"]/span[@class="see-more inline"]/a/@href')[0]
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
