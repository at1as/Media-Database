#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import lxml.html
import os
import jinja2

base_url = "http://www.imdb.com"
search_path = "/find?q="
asset_location = "/"
exclude_formats = ["srt", "jpeg", "jpg", "png", "txt", "rtf", "py", "pyc", "ini", "frm", "css", "html", "htm", "DS_Store", "conf"]

# Environment for static html generation
env = jinja2.Environment(loader=jinja2.FileSystemLoader(["./_templates"]))
index = env.get_template("index.html")
about = env.get_template("about.html")
filter_index = env.get_template("filter.html")
movie_details = env.get_template("movie_details.html")


# Check specified path for files, and filter out unwanted content before returning
def get_movie_list(path = "./"):
  stored_files = os.listdir(u"%s" % path)
  stored_movies = []
  for file in stored_files:
    # Remove all hidden file types (files that begin with "." or "_"), and explicitly excluded file types
    if file.split(".")[-1:][0] not in exclude_formats and file[0] not in [".", "_"]:
      # Add the file (removing the file extension)
      stored_movies.append("".join(file.split(".")[0:-1]))
  #print("1. STORED MOVIES:", stored_movies)#TEMP:
  return stored_movies


# Construct search results url for specified movie
def construct_search_url(movie):
  #print("2. SEARCH URL:", base_url + search_path + movie.replace(" ", "+").lower()) #TEMP
  #print "3. SEARCH URL (ENC):", u'%s' %(base_url + search_path + movie.replace(" ", "+").lower())
  return u'%s' %(base_url + search_path + movie.replace(" ", "+").lower())


# Return the URL corresponding to particular movie
def get_movie_url(movie):
  # TODO: ensure that search results are from titles, rather than characters, etc
  search_url = construct_search_url(movie)
  print "SURL:", search_url, type(search_url)
  print "SURL ENC ", u'%s' % search_url, type(u'%s' % search_url)
  print "SURL Eu", unicode(search_url), type(unicode(search_url))
  search_results = requests.get(search_url)
  print 'SR:', search_results.url, type(search_results.url)
  print 'SR:', u'%s' % search_results.url
  page = lxml.html.document_fromstring(requests.get(construct_search_url(movie)).content)
  endpoint = page.xpath('//*[@id="main"]/div[1]/div[2]/table[1]/tr/td/a')[0].attrib['href']
  print "BASE_URL + END POINT:" + base_url + endpoint
  return base_url + endpoint


# Scrape movie page for attributes specified below
def get_movie_details(movie):
  movie_attributes = {}
  movie_page = lxml.html.document_fromstring(requests.get(get_movie_url(movie)).content)
  try:
    movie_attributes['title'] = movie_page.xpath('//*[@id="overview-top"]/h1/span[1]/text()')[0].strip()
  except IndexError:
    movie_attributes['title'] = ""
  try:
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
    movie_attributes['languages'] = movie_page.xpath('//*[@id="titleDetails"]/div[3]/a/text()')
  except IndexError:
    movie_attributes['languages'] = ""
  return movie_attributes


# Create list of movie attributes
def compile_movie_list():
  movie_attributes_list = []
  for movie in get_movie_list():
    movie_attributes_list.append(get_movie_details(movie))
  return movie_attributes_list


def generate_site():
  final_list = compile_movie_list()

  # List Page
  list_page = index.render(movie_list = final_list)
  f = open("_output/index.html", "w")
  f.write(list_page.encode('utf-8'))
  f.close

  # Filer Page
  filter_page = filter_index.render(movie_list = final_list)
  j = open("_output/filter.html", "w")
  j.write(filter_page)
  j.close

  # About Page
  about_page = about.render(number_of_movies = len(final_list))
  g = open("_output/about.html", "w")
  g.write(about_page.encode('utf-8'))
  g.close

  # Individual Title Pages
  for item in final_list:
    output_dir = "_output/%s(%s).html" %(item['title'], item['year'])
    movie_page = movie_details.render(number_of_movies = len(final_list), movie = item)
    h = open(output_dir, "w")
    h.write(movie_page.encode('utf-8'))
    h.close

generate_site()
