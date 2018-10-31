#!/usr/bin/env python
# -*- coding: utf8 -*-


from ..helpers import HEADERS
from .base_scraper import BaseScraper
import lxml.html
import requests
import time
from unicodedata import normalize


class IMDB(BaseScraper):
  BASE_URL = "http://www.imdb.com"
  SEARCH_PATH = "/find?q="
  URL_END = "&s=all"

  def __init__(self):
    pass

  def construct_search_url(self, title):
    """ Construct search results url for specified title """
    safe_title = normalize("NFC", title).replace(" ", "+").replace("&", "%26").replace("?", "%3F").lower()
    return "{}{}{}{}".format(IMDB.BASE_URL, IMDB.SEARCH_PATH, safe_title, IMDB.URL_END)

  def get_title(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="title_block"]//h1/text()')[0].strip()
    except IndexError:
      return ''

  def get_alternative_title(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="title_wrapper"]//div[@class="originalTitle"]/text()')
    except IndexError:
      return ''

  def get_description(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="summary_text"]')[0].text_content().strip().replace('See full summary', '').replace('»', '').strip()
    except IndexError:
      return ''

  def get_director(self, xml_doc):
    try:
      return [x.text for x in xml_doc.xpath('//div[@class="plot_summary_wrapper"]//div[@class="credit_summary_item"][1]//a')]
    except IndexError:
      return ''

  def get_rating(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="ratingValue"]/strong/span/text()')[0].strip()
    except IndexError:
      return ''

  def get_genres(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="titleBar"]//div[@class="title_wrapper"]/div[@class="subtext"]/a/text()')[0:-1]
    except IndexError:
      return ''

  def get_votes(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="imdbRating"]/a/span/text()')[0].strip()
    except IndexError:
      return ''

  def get_running_time(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="titleBar"]//div[@class="title_wrapper"]//time/text()')[0].strip()
    except IndexError:
      return ''

  def get_content_rating(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="titleBar"]/div[2]/div[@class="subtext"]/text()')[0].strip()
    except IndexError:
      return ''

  def get_stars(self, xml_doc):
    try:
      return [x.text for x in xml_doc.xpath('//div[@class="plot_summary_wrapper"]//div[@class="credit_summary_item"][3]//a')][0:-1]
    except IndexError:
      try:
        return xml_doc.xpath('//div[@class="plot_summary_wrapper"]/div[1]/div[3]/span/a/span/text()')
      except IndexError:
        return ''

  def get_languages(self, xml_doc):
    try:
      if xml_doc.xpath('//*[@id="titleDetails"]/div[3]/h4/text()') == ['Language:']:
        return xml_doc.xpath('//*[@id="titleDetails"]/div[3]/a/text()')
      else:
        return xml_doc.xpath('//*[@id="titleDetails"]/div[2]/a/text()')
    except IndexError:
      return ''

  def get_image_url(self, xml_doc):
    try:
      return xml_doc.xpath('//*[@class="poster"]/a/img/@src')[0]
    except IndexError:
      return ''

  # Movie specific functions
  def get_movie_year(self, xml_doc):
    try:
      return xml_doc.xpath('//*[@class="title_wrapper"]//span[@id="titleYear"]/a/text()')[0]
    except IndexError:
      return ''

  def get_awards(self, xml_doc):
    try:
      awards = xml_doc.xpath('//*[@id="titleAwardsRanks"]/span[@class="awards-blurb"]/b/text()')[0].strip()
      if not "oscar" in awards.lower():
        return ''
      else:
        if awards[-1] == ".":
          return " ".join(xml_doc.xpath('//div[@id="titleAwardsRanks"]//span[@class="awards-blurb"]/b/text()')[0].strip().split())
        try:
          return IMDB.BASE_URL + xml_doc.xpath('//*[@id="titleAwardsRanks"]/span[@class="see-more inline"]/a/@href')[0]
        except IndexError:
          return ''
    except IndexError:
      return ''

  # Series Specific Functions
  def get_series_year(self, xml_doc):
    try:
      return xml_doc.xpath('//div[@class="title_wrapper"]//div[@class="subtext"]/a/text()')[-1].strip().split('(')[-1].split(')')[0].strip()
    except IndexError:
      return ''

  def get_creator(self, xml_doc):
    try:
      return [x.text for x in xml_doc.xpath('//div[@class="plot_summary_wrapper"]//div[@class="credit_summary_item"][1]//a')]
    except IndexError:
      return ''

  def get_series_stars(self, xml_doc):
    try:
      return [x.text for x in xml_doc.xpath('//div[@class="plot_summary_wrapper"]//div[@class="credit_summary_item"][2]//a')][0:-1]
    except IndexError:
      return ''

  # Full Response Payloads

  def get_search_page(self, asset):
    """
      Get search page listing all matching titles (from which the url of the title will be extracted)
    """
    search_url = self.construct_search_url(asset)
    return lxml.html.document_fromstring(requests.get(search_url, headers=HEADERS).content)


  def get_movie_page_url(self, title):
    """
      return URL associated with movie page by parsing search page DOM
      return None if no results are found
    """
    invalid_results = ["(TV Episode)", "(TV Series)", "(TV Mini-Series)", "(Short)", "(Video Game)"]
    search_page = self.get_search_page(title)

    try:
      for index, section in enumerate(search_page.xpath('//*[@id="main"]/div[1]/div')):
        if len(section.xpath('h3/text()')) > 0:

          # Find the Div associated with Titles (rather than Characters, etc)
          if section.xpath('h3/text()')[0] == "Titles":

            # Select first in list which doesn't contain invalid_results
            for index, list_title in enumerate(search_page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr')):
              if not any(x in list_title.text_content() for x in invalid_results):
                endpoint = search_page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr[%i]/td/a' %(index+1))[0].attrib['href']
                return IMDB.BASE_URL + endpoint
    except IndexError:
      return


  def get_series_page_url(self, title):
    """
      return URL associated with series page by parsing search page DOM
      return None if no results are found
    """
    valid_results = ["(TV Series)", "(TV Mini-Series)"]
    search_page = self.get_search_page(title)

    try:
      for index, section in enumerate(search_page.xpath('//*[@id="main"]/div[1]/div')):
        if len(section.xpath('h3/text()')) > 0:

          # Find the Div associated with Titles (rather than Characters, etc)
          if section.xpath('h3/text()')[0] == "Titles":

            # Select first in list which doesn't contain invalid_results
            for index, list_title in enumerate(search_page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr')):
              if any(x in list_title.text_content() for x in valid_results):

                # Some items listed as "TV Episode" also contain a link with the term "TV Series" below
                if "(TV Episode)" not in list_title.text_content():
                  endpoint = search_page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr[%i]/td/a' %(index+1))[0].attrib['href']
                  return IMDB.BASE_URL + endpoint
    except IndexError:
      return None


  def get_movie_details(self, movie, movie_url):
    """ Scrape movie page for attributes specified below """

    if movie_url != None:
      movie_page = lxml.html.document_fromstring(requests.get(movie_url, headers=HEADERS).content)

      return {
        'url':                movie_url,
        'info_retrieved':     time.strftime("%Y-%m-%d"),
        'title':              self.get_title(movie_page),
        'alternative_title':  self.get_alternative_title(movie_page),
        'year':               self.get_movie_year(movie_page),
        'description':        self.get_description(movie_page),
        'director':           self.get_director(movie_page),
        'stars':              self.get_stars(movie_page),
        'genre':              self.get_genres(movie_page),
        'rating':             self.get_rating(movie_page),
        'votes':              self.get_votes(movie_page),
        'running_time':       self.get_running_time(movie_page),
        'languages':          self.get_languages(movie_page),
        'content_rating':     self.get_content_rating(movie_page),
        'awards':             self.get_awards(movie_page),
        'image_url':          self.get_image_url(movie_page),
      }


  def get_series_details(self, series, series_url):
    """ Scrape series page for attributes specified below """

    if series_url != None:
      series_page = lxml.html.document_fromstring(requests.get(series_url, headers=HEADERS).content)

      return {
        'url':            series_url,
        'info_retrieved': time.strftime("%Y-%m-%d"),
        'title':          self.get_title(series_page),
        'year':           self.get_series_year(series_page),
        'description':    self.get_description(series_page),
        'creator':        self.get_creator(series_page),
        'stars':          self.get_series_stars(series_page),
        'genre':          self.get_genres(series_page),
        'rating':         self.get_rating(series_page),
        'votes':          self.get_votes(series_page),
        'running_time':   self.get_running_time(series_page),
        'languages':      self.get_languages(series_page),
        'content_rating': self.get_content_rating(series_page),
        'image_url':      self.get_image_url(series_page),
      }
