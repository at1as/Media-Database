#!/usr/bin/env python
# -*- coding: utf8 -*-

from  __future__ import unicode_literals
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
    try:
      movie_attributes['title'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[1]/text()')[0].strip()
    except IndexError:
      movie_attributes['title'] = ""
    try:
      movie_attributes['alternative_title'] = movie_page.xpath('//*[@class="title-extra"]/text()')[0].strip()
    except IndexError:
      movie_attributes['alternative_title'] = ""
    try:
      if movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip() != "(":
        if movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip() not in ["(I)", "(II)", "(III)", "(IV)", "(V)"]:
          movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip()[1:-1]
        else:
          movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[3]/a/text()')[0].strip()
      else:
        movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/a/text()')[0].strip()
    except IndexError:
      try:
        movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[3]/a/text()')[0].strip()
      except IndexError:
        movie_attributes['year'] = ""
    try:
      movie_attributes['description'] = movie_page.xpath('//*[@id="overview-top"]/p[2]')[0].text_content().strip().replace('See full summary', '')
    except IndexError:
      movie_attributes['description'] = ""
    try:
      movie_attributes['director'] = movie_page.xpath('//*[@id="overview-top"]/div[4]/a/span/text()')[0].strip()
    except IndexError:
      movie_attributes['director'] = ""
    try:
      movie_attributes['stars'] = movie_page.xpath('//*[@id="overview-top"]/div[@itemprop="actors"]/a/span/text()')
    except IndexError:
      movie_attributes['stars'] = ""
    try:
      movie_attributes['genre'] = movie_page.xpath('//*[@id="overview-top"]/div[@class="infobar"]/a/span/text()')
    except IndexError:
      movie_attributes['genre'] = ""
    try:
      movie_attributes['rating'] = movie_page.xpath('//span[@itemprop="ratingValue"]/text()')[0].strip()
    except IndexError:
      movie_attributes['rating'] = ""
    try:
      movie_attributes['votes'] = movie_page.xpath('//span[@itemprop="ratingCount"]/text()')[0].strip()
    except IndexError:
      movie_attributes['votes'] = ""
    try:
      movie_attributes['running_time'] = movie_page.xpath('//time[@itemprop="duration"]/text()')[0].strip()
    except IndexError:
      movie_attributes['running_time'] = ""
    try:
      if movie_page.xpath('//*[@id="titleDetails"]/div[3]/h4/text()') == ['Language:']:
        movie_attributes['languages'] = movie_page.xpath('//*[@id="titleDetails"]/div[3]/a/text()')
      else:
        movie_attributes['languages'] = movie_page.xpath('//*[@id="titleDetails"]/div[2]/a/text()')
    except IndexError:
      movie_attributes['languages'] = ""
    try:
      movie_attributes['content_rating'] = movie_page.xpath('//meta[@itemprop="contentRating"]')[0].attrib['content'].strip()
    except IndexError:
      movie_attributes['content_rating'] = ""
    try:
      movie_attributes['awards'] = movie_page.xpath('//*[@id="titleAwardsRanks"]/span[@itemprop="awards"]/b/text()')[0]
      if not "oscar" in movie_attributes['awards'].lower():
        movie_attributes['awards'] = ""
      else:
        if movie_attributes['awards'][-1:] == ".":
          movie_attributes['awards'] = movie_attributes['awards'][:-1]
        try:
          movie_attributes['awards_link'] = config['base_url'] + movie_page.xpath('//*[@id="titleAwardsRanks"]/span[@class="see-more inline"]/a/@href')[0]
        except IndexError:
          movie_attributes['awards_link'] = ""
    except IndexError:
      movie_attributes['awards'] = ""
    try:
      movie_attributes['image_url'] = movie_page.xpath('//*[@id="img_primary"]/div[1]/a[1]/img/@src')[0]
      save_image(movie_attributes['image_url'], movie_attributes['filename'], mediatype)
    except IndexError:
      movie_attributes['image_url'] = ""
    return movie_attributes
  else:
    return None


def get_series_details(movie, mediatype):
  # Scrape series page for attributes specified below
  
  movie_attributes = {}
  movie_url = get_title_url(movie['name'], mediatype)

  if movie_url != None:
    movie_page = lxml.html.document_fromstring(requests.get(movie_url, headers=headers).content)

    movie_attributes['url'] = movie_url
    movie_attributes['filename'] = movie['name']
    movie_attributes['extension'] = movie['extension']
    movie_attributes['info_retrieved'] = time.strftime("%Y-%m-%d")
    try:
      movie_attributes['title'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[1]/text()')[0].strip()
    except IndexError:
      movie_attributes['title'] = ""
    try:
      if movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip() != "(":
        if movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip() not in ["(I)", "(II)", "(III)", "(IV)", "(V)"]:
          movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip()[1:-1]
        else:
          movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[3]/text()')[0].strip()[1:-1]
      else:
        movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip()[1:-1]
    except IndexError:
      try:
        movie_attributes['year'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[3]/text()')[0].strip()[1:-1]
      except IndexError:
        movie_attributes['year'] = ""
    try:
      movie_attributes['description'] = movie_page.xpath('//*[@id="overview-top"]/p[2]')[0].text_content().strip().replace('See full summary', '')
    except IndexError:
      movie_attributes['description'] = ""
    try:
      if movie_page.xpath('//*[@id="overview-top"]/div[3]/h4/text()')[0].strip() == "Creator:":
        movie_attributes['creator'] = movie_page.xpath('//*[@id="overview-top"]/div[3]/a/span/text()')[0].strip()
      else:
        movie_attributes['creator'] = ""
    except IndexError:
      movie_attributes['creator'] = ""
    try:
      if movie_page.xpath('//*[@id="overview-top"]/div[3]/h4/text()')[0].strip() == "Stars:":
        movie_attributes['stars'] = movie_page.xpath('//*[@id="overview-top"]/div[3]/a/span/text()')
      else:
        movie_attributes['stars'] = movie_page.xpath('//*[@id="overview-top"]/div[4]/a/span/text()')
    except IndexError:
      try:
        movie_attributes['stars'] = movie_page.xpath('//*[@id="overview-top"]/div[@itemprop="actors"]/a/span/text()')
      except IndexError:
        movie_attributes['stars'] = ""
    try:
      movie_attributes['genre'] = movie_page.xpath('//*[@id="overview-top"]/div[@class="infobar"]/a/span/text()')
    except IndexError:
      movie_attributes['genre'] = ""
    try:
      movie_attributes['rating'] = movie_page.xpath('//*[@class="titlePageSprite star-box-giga-star"]/text()')[0].strip()
    except IndexError:
      movie_attributes['rating'] = ""
    try:
      movie_attributes['votes'] = movie_page.xpath('//*[@itemprop="ratingCount"]/text()')[0].strip()
    except IndexError:
      movie_attributes['votes'] = ""
    try:
      movie_attributes['running_time'] = movie_page.xpath('//*[@id="overview-top"]/div[@class="infobar"]/time/text()')[0].strip()
    except IndexError:
      movie_attributes['running_time'] = ""
    try:
      if movie_page.xpath('//*[@id="titleDetails"]/div[3]/h4/text()') == ['Language:']:
        movie_attributes['languages'] = movie_page.xpath('//*[@id="titleDetails"]/div[3]/a/text()')
      else:
        movie_attributes['languages'] = movie_page.xpath('//*[@id="titleDetails"]/div[2]/a/text()')
    except IndexError:
      movie_attributes['languages'] = ""
    try:
      movie_attributes['content_rating'] = movie_page.xpath('//*[@class="infobar"]/meta[1]/@content')[0].strip()
    except IndexError:
      movie_attributes['content_rating'] = ""
    try:
      movie_attributes['image_url'] = movie_page.xpath('//*[@id="img_primary"]/div[1]/a[1]/img/@src')[0]
      save_image(movie_attributes['image_url'], movie_attributes['filename'], mediatype)
    except IndexError:
      movie_attributes['image_url'] = ""
    return movie_attributes
  else:
    return None
