#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import unicode_literals

import requests
import lxml.html
import os
import jinja2
import json
import simplejson
import shutil
import urllib
import time
from datetime import datetime
from unicodedata import normalize


# Input Environment Configuration
with open('conf.json') as config_json:
  config = json.load(config_json)

# Initialise Empty Movie Dictionary (if not present)
if not os.path.isfile('movie_data.json'):
  with open("movie_data.json", "w+") as movie_feed:
    json.dump({}, movie_feed)

# Output Environment for static html generation
env = jinja2.Environment(loader=jinja2.FileSystemLoader(["./_templates"]))
index = env.get_template("index.html")
about = env.get_template("about.html")
movie_details = env.get_template("movie_details.html")


# Check specified path for files, and filter out unwanted content before returning
def get_movie_list(path):
  movie_list = os.listdir(path)[0:config["max_quantity"]]
  filtered_movie_list = []

  for file in movie_list:
    # If the extension is in include_extension, or file is a folder not preceded by '_'
    if file.split(".")[-1:][0] in config["include_extensions"] or (len(file.split(".")) == 1 and file[0] != "_" and file not in config["exclude_files"]):

      movie_title = file.rsplit(".", 1)[0]

      # Add the file if it is not already in
      with open("movie_data.json", 'r') as saved_movie_list:
        saved_movies = json.load(saved_movie_list)

        # Do not repeat scrape for already acquired title
        if not saved_movies.has_key(movie_title):
          print "Now adding: %s" % movie_title
          filtered_movie_list.append(movie_title)
  return filtered_movie_list


# Construct search results url for specified movie
def construct_search_url(movie):
  safe_movie = normalize("NFC", movie).replace(" ", "+").replace("&", "%26").lower()
  return config["base_url"] + config["search_path"] + safe_movie + config["url_end"]

# Return the URL corresponding to particular movie
def get_movie_url(movie):
  search_url = construct_search_url(movie)
  page = lxml.html.document_fromstring(requests.get(search_url).content)
  try:
    if page.xpath('//*[@id="main"]/div[1]/div[2]/h3/text()')[0] == "Titles":
      endpoint = page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr/td/a')[0].attrib['href']
      return config["base_url"] + endpoint
  except IndexError: pass
  try:
    if page.xpath('//*[@id="main"]/div[1]/div[3]/h3/text()')[0] == "Titles":
      endpoint = page.xpath('//*[@id="main"]/div[1]/div[3]/table[1]/tr/td/a')[0].attrib['href']
      return config["base_url"] + endpoint
  except IndexError: pass
  try:
    if page.xpath('//*[@id="main"]/div[1]/div[4]/h3/text()')[0] == "Titles":
      endpoint = page.xpath('//*[@id="main"]/div[1]/div[4]/table[1]/tr/td/a')[0].attrib['href']
      return config["base_url"] + endpoint
  except IndexError: pass
  try:
    if page.xpath('//*[@id="main"]/div[1]/div[5]/h3/text()')[0] == "Titles":
      endpoint = page.xpath('//*[@id="main"]/div[1]/div[5]/table[1]/tr/td/a')[0].attrib['href']
      return config["base_url"] + endpoint
  except IndexError: pass
  try:
    if page.xpath('//*[@id="main"]/div[1]/div[6]/h3/text()')[0] == "Titles":
      endpoint = page.xpath('//*[@id="main"]/div[1]/div[6]/table[1]/tr/td/a')[0].attrib['href']
      return config["base_url"] + endpoint
  except IndexError:
    print "***SKIPPING: %s" % movie
    return None


# Scrape movie page for attributes specified below
def get_movie_details(movie):
  movie_attributes = {}
  movie_url = get_movie_url(movie)
  if movie_url != None:
    movie_page = lxml.html.document_fromstring(requests.get(movie_url).content)

    movie_attributes['url'] = movie_url
    movie_attributes['filename'] = movie
    movie_attributes['info_retrieved'] = time.strftime("%Y-%m-%d")
    try:
      movie_attributes['title'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[1]/text()')[0].strip()
    except IndexError:
      movie_attributes['title'] = ""
    try:
      if movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip() != "(":
        if movie_page.xpath('//*[@id="overview-top"]/h1/span[2]/text()')[0].strip() != "(I)":
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
      movie_attributes['description'] = movie_page.xpath('//*[@id="overview-top"]/p[2]/text()')[0].strip()
    except IndexError:
      movie_attributes['description'] = ""
    try:
      movie_attributes['director'] = movie_page.xpath('//*[@id="overview-top"]/div[4]/a/span/text()')[0].strip()
    except IndexError:
      movie_attributes['director'] = ""
    try:
      movie_attributes['stars'] = movie_page.xpath('//*[@id="overview-top"]/div[6]/a/span/text()')
    except IndexError:
      movie_attributes['stars'] = ""
    try:
      movie_attributes['genre'] = movie_page.xpath('//*[@id="overview-top"]/div[2]/a/span/text()')
    except IndexError:
      movie_attributes['genre'] = ""
    try:
      movie_attributes['rating'] = movie_page.xpath('//*[@id="overview-top"]/div[3]/div[3]/strong/span/text()')[0]
    except IndexError:
      movie_attributes['rating'] = ""
    try:
      movie_attributes['votes'] = movie_page.xpath('//*[@id="overview-top"]/div[3]/div[3]/a[1]/span/text()')[0].strip()
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
      movie_attributes['content_rating'] = movie_page.xpath('//*[@class="infobar"]/span[1]/@content')
    except IndexError:
      movie_attributes['content_rating'] = ""
    try:
      movie_attributes['image_url'] = movie_page.xpath('//*[@id="img_primary"]/div[1]/a[1]/img/@src')[0]
      save_image(movie_attributes['image_url'], movie_attributes['filename'])
    except IndexError:
      movie_attributes['image_url'] = ""
    return movie_attributes
  else:
    return None

# If image_url was found, write image to directory
def save_image(url, name):
  img = requests.get(url, stream=True)
  if img.status_code == 200:
    with open('_output/images/' + name + '.png', 'wb') as f:
        img.raw.decode_content = True
        shutil.copyfileobj(img.raw, f)


# Create list of movie attributes
def compile_movie_list():
  movie_attributes_list = []
  for movie in get_movie_list(config["asset_location"]):
    movie_attributes = get_movie_details(movie)
    if movie_attributes != None:
      movie_attributes_list.append(movie_attributes)
  return movie_attributes_list


def generate_site(additional_movies):

  # Import Data from JSON file
  with open("movie_data.json", 'r') as movie_feed:
    saved_movies = json.load(movie_feed)

  # Add new saved movies to JSON file
  for movie in additional_movies:
    saved_movies[movie['filename']] = movie

  # Write contents to JSON file
  with open("movie_data.json", 'w+') as movie_feed:
    json.dump(saved_movies, movie_feed, encoding="utf-8")

  # List Page
  list_page = index.render(movie_list = saved_movies)
  f = open("_output/index.html", "w")
  f.write(list_page.encode('utf-8'))
  f.close

  # About Page
  about_page = about.render(number_of_movies = len(saved_movies), time = str(datetime.now()))
  g = open("_output/about.html", "w")
  g.write(about_page.encode('utf-8'))
  g.close

  # Individual Title Pages
  for item in saved_movies:
    output_dir = "_output/pages/%s(%s).html" %(saved_movies[item]['title'].replace('/', ''), saved_movies[item]['year'])
    movie_page = movie_details.render(number_of_movies = len(saved_movies), movie = saved_movies[item])
    h = open(output_dir, "w")
    h.write(movie_page.encode('utf-8'))
    h.close


generate_site(compile_movie_list())
