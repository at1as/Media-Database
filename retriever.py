#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals
from datetime import datetime
from unicodedata import normalize
import jinja2
import json
import lxml.html
import os
import pdb
import requests
import simplejson
import shutil
import time
import urllib

# Change User Agent header from Requests to Mozilla for requests made to IMDB
headers={ "User-Agent": "Mozilla/5.0",
          "Accept-Language": "en-US,en;q=0.8"}

# Import Input Environment Configuration and Validation
try:
  with open('conf.json') as config_json:
    config = json.load(config_json)
  
  if config["include_extensions"] == []:
    print "\nWarning: No extensions specified in include_extensions in conf.json. Will not currently scrape for any filetypes"
  if config["base_url"] != "http://www.imdb.com" or config["search_path"] != "/find?q=" or config["url_end"] != "&s=all":
    print "\nWarning: base_url, search_path and url_end have been changed from their defaults in conf.json. Proceed at your own risk"
  
  for asset_type in config["assets"]:
    if config["assets"][asset_type]["saved_data"] == "":
      print "\nError: Please specify a path for the assets.%s.saved_data repository in conf.json" % asset_type
      raise SystemExit
    if not type(config["assets"][asset_type]["max_assets"]) is int or config["assets"][asset_type]["max_assets"] < 0:
      print "\nError: Please specify a valid integer for assets.%s.max_quantity repository in conf.json" % asset_type
      raise SystemExit  
    if config["assets"][asset_type]["index_asset"] and config["assets"][asset_type]["location"] == "":
      print "\nError: \"%s\" is set to index files, but path to directory is not specified in conf.json\n" % asset_type
      raise SystemExit
except:
  print "\nError: Invalid JSON body in conf.json.\nSee: http://jsonformatter.curiousconcept.com/ for assistance\n"
  raise SystemExit


# Create empty datafiles if not present
def initialize_asset_repo(base_path, mediatype):
  
  if not os.path.isfile(config['assets'][base_path]['saved_data']):
    with open(config['assets'][base_path]['saved_data'], 'w+') as item_feed:
      json.dump({}, item_feed)

  if config['assets'][base_path]['index_asset']:
    item_list = compile_file_list(config['assets'][base_path]['location'], config['assets'][base_path]['saved_data'], mediatype)    
  else:
    item_list = []

  return item_list


def get_file_list(path, repo, mediatype):
  # TODO: enforce limit per asset (rather than deprecated global limit)
  try:
    if not config["max_assets"] == 0:
      file_list = os.listdir(path)[0:config["max_assets"]]
    else:
      file_list = os.listdir(path)
  except OSError:
    print "\nError: Path \"%s\" not found. Specify a valid path in conf.json and ensure all directories on this path exist.\n" % path
    raise SystemExit
  
  filtered_file_list = []

  for file in file_list:

    # If the extension is in include_extension, or file is a folder not preceded by '_'
    if ((os.path.isfile(path + file) and file.split(".")[-1:][0] in config["include_extensions"]) or (os.path.isdir(path + file) and file[0] != "_")) and file not in config["exclude_files"]: 

      # Strip extension from file
      if os.path.isfile(path + file):
        file_title = file.rsplit(".", 1)[0]
      else:
        file_title = file

      # Drop prepending "._" from files on external drives
      if file_title[0:2] == "._":
        file_title = file_title[2:]

      # Add the file if it is not already in
      with open(repo, 'r') as saved_file_list:
        saved_files = json.load(saved_file_list)

        # Do not repeat scrape for already acquired title
        if not saved_files.has_key(file_title):
          #print "Now adding: \"%s\"" % file_title
          print "Now adding: %s : %s" %(path, file_title)
          filtered_file_list.append(file_title)
  return filtered_file_list


# Construct search results url for specified title
def construct_search_url(title):
  safe_title = normalize("NFC", title).replace(" ", "+").replace("&", "%26").replace("?", "%3F").lower()
  return config["base_url"] + config["search_path"] + safe_title + config["url_end"]


# Return the URL corresponding to particular title
def get_title_url(asset, mediatype):
  
  if mediatype == "movie":
    invalid_results = ["(TV Episode)", "(TV Series)", "(TV Mini-Series)"]
  elif mediatype =="series":
    valid_results = ["(TV Series)", "(TV Mini-Series)"]

  search_url = construct_search_url(asset)
  page = lxml.html.document_fromstring(requests.get(search_url, headers=headers).content)

  try:
    for index, section in enumerate(page.xpath('//*[@id="main"]/div[1]/div')):
      if len(section.xpath('h3/text()')) > 0:

        # Find the Div associated with Titles (rather than Characters, etc)
        if section.xpath('h3/text()')[0] == "Titles":

          # Select first in list which doesn't contain invalid_results
          for index, list_title in enumerate(page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr')):

            # Movies in list have no tag
            if mediatype == "movie":
              if not any(x in list_title.text_content() for x in invalid_results):
                endpoint = page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr[%i]/td/a' %(index+1))[0].attrib['href']
                return config["base_url"] + endpoint
            
            # Series in list are tagged
            elif mediatype == "series":
              if any(x in list_title.text_content() for x in valid_results):

                # Some items listed as "TV Episode" also contain a link with the term "TV Series" below
                if "(TV Episode)" not in list_title.text_content():
                  endpoint = page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr[%i]/td/a' %(index+1))[0].attrib['href']
                  return config["base_url"] + endpoint

    # If not found, return None
    print "Warn: \"%s\" not found. Skipping." % asset
    return None
  except IndexError:
    print "Warn: \"%s\" not found. Skipping." % asset
    return None


# Scrape movie page for attributes specified below
def get_movie_details(movie, mediatype):
  movie_attributes = {}
  movie_url = get_title_url(movie, mediatype)

  if movie_url != None:
    movie_page = lxml.html.document_fromstring(requests.get(movie_url, headers=headers).content)

    movie_attributes['url'] = movie_url
    movie_attributes['filename'] = movie
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
      movie_attributes['description'] = movie_page.xpath('//*[@id="overview-top"]/p[2]')[0].text_content().strip()
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

# Scrape series page for attributes specified below
def get_series_details(movie, mediatype):
  movie_attributes = {}
  movie_url = get_title_url(movie, mediatype)

  if movie_url != None:
    movie_page = lxml.html.document_fromstring(requests.get(movie_url, headers=headers).content)

    movie_attributes['url'] = movie_url
    movie_attributes['filename'] = movie
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
      movie_attributes['description'] = movie_page.xpath('//*[@id="overview-top"]/p[2]')[0].text_content().strip()
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
      movie_attributes['genre'] = movie_page.xpath('//*[@id="overview-top"]/div[2]/a/span/text()')
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
      movie_attributes['running_time'] = movie_page.xpath('//*[@id="overview-top"]/div[2]/time/text()')[0].strip()
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


# If image_url was found, write image to directory
# TODO: image directory per asset type (ex. _output/movies/images, etc)
def save_image(url, name, mediatype):
  img = requests.get(url, headers=headers, stream=True)
  if img.status_code == 200:
    with open('_output/images/' + name + '.png', 'wb') as f:
      img.raw.decode_content = True
      shutil.copyfileobj(img.raw, f)


def compile_file_list(path, repo, mediatype):
  file_attributes_list = []

  for file in get_file_list(path, repo, mediatype):

    if mediatype == "movie":
      file_attributes = get_movie_details(file, "movie")
    elif mediatype == "series":
      file_attributes = get_series_details(file, "series")
    
    if file_attributes != None:
      file_attributes_list.append(file_attributes)
   
  return file_attributes_list


def write_scraped_data(base_path, additional_assets):
  
  # Import Data from JSON file
  with open(config['assets'][base_path]['saved_data'], 'r') as asset_feed:
    saved_assets = json.load(asset_feed)

  if additional_assets != []:
    
    # Add new saved assets to JSON file
    for asset in additional_assets:
      saved_assets[asset['filename']] = asset

    # Write combined asset contents to JSON file
    with open(config['assets'][base_path]['saved_data'], 'w+') as asset_feed:
      json.dump(saved_assets, asset_feed, encoding="utf-8")
  
  return saved_assets


def generate_site(additional_movies, additional_series):

  saved_movies  = write_scraped_data("movies", additional_movies)
  saved_series  = write_scraped_data("series", additional_series)
  num_movies    = len(saved_movies)
  num_series    = len(saved_series)

  # Output Environment for static html generation
  env             = jinja2.Environment(loader=jinja2.FileSystemLoader(["./_templates"]))
  index           = env.get_template("index.html")
  series          = env.get_template("series.html")
  about           = env.get_template("about.html")
  movie_details   = env.get_template("movie_details.html")
  series_details  = env.get_template("series_details.html")


  # Movie Index Page
  movies_page = index.render(movie_list = saved_movies, number_of_series = num_series)
  f = open("_output/index.html", "w")
  f.write(movies_page.encode('utf-8'))
  f.close

  # TV Series Page
  series_page = series.render(series_list = saved_series, number_of_movies = num_movies)
  j = open("_output/series.html", "w")
  j.write(series_page.encode('utf-8'))
  j.close

  # About Page
  about_page = about.render(number_of_movies = num_movies, number_of_series = num_series, time = str(datetime.now()))
  g = open("_output/about.html", "w")
  g.write(about_page.encode('utf-8'))
  g.close

  # Individual Movie Pages
  for item in saved_movies:
    output_dir = "_output/movies/%s(%s).html" %(saved_movies[item]['title'].replace('/', ''), saved_movies[item]['year'])
    movie_page = movie_details.render(number_of_movies = num_movies, movie = saved_movies[item], number_of_series = num_series)
    h = open(output_dir, "w")
    h.write(movie_page.encode('utf-8'))
    h.close

  # Individual Series Page
  for item in saved_series:
    output_dir = "_output/series/%s(%s).html" %(saved_series[item]['title'].replace('/', ''), saved_series[item]['year'][0:4])
    series_page = series_details.render(number_of_series = num_series, series = saved_series[item], number_of_movies = num_movies)
    k = open(output_dir, "w")
    k.write(series_page.encode('utf-8'))
    k.close


if __name__ == "__main__":

  movie_list  = initialize_asset_repo("movies", "movie")
  series_list = initialize_asset_repo("series", "series")

  generate_site(movie_list, series_list)

