#!/usr/bin/env python
# -*- coding: utf8 -*-

# Remove saved entries from movie_data.json
# Useful for entries that have been tagged incorrectly

from __future__ import unicode_literals

import os
import sys
import json
from unicodedata import normalize

DATA = 'movie_data.json'
HELP = '\nUsage: \n\tpython remove_entry.py "<filename>"\n\nExample: \n\tpython remove_entry.py "Monty Python and the Holy Grail"\n'

def remove_file(movie_name):
  if os.path.isfile(DATA):

    found = False

    # Read contents of JSON file
    with open("movie_data.json", 'r') as saved_movie_list:
      saved_movies = json.load(saved_movie_list)

    # Delete entry
    try:
      for key in saved_movies:
        if saved_movies[key]['title'].lower() == movie_name.lower():
          del saved_movies[key]
          found = True
          break
      if not found:
        print "\nEntry not found: %s in saved movies\n" % movie_name
        return
    except KeyError:
      print "\nEntry not found: %s in saved movies\n" % movie_name
      return

    # Write contents to JSON file
    with open("movie_data.json", 'w+') as movie_feed:
      json.dump(saved_movies, movie_feed, encoding="utf-8")
  
    print "\nEntry deleted: %s\n" % movie_name
    return

  else:
    print "\nFile not found: %s\n" % DATA
    return


if __name__ == "__main__":
  try:
    if sys.argv[1] in ["-h", "--help", "--h", " "]:
      print HELP
    else:
      remove_file(normalize("NFC", sys.argv[1].decode('UTF-8')))
  except IndexError:
    print HELP

