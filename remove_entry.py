#!/usr/bin/env python
# -*- coding: utf8 -*-

# Remove saved entries from saved json repositories
# Useful for entries that have been tagged incorrectly

from __future__ import unicode_literals

import os
import sys
import json
from unicodedata import normalize


# Import Environment Configuration
try:
  with open('conf.json') as config_json:
    config = json.load(config_json)
except:
  print "\nInvalid JSON body in conf.json\nSee: http://jsonformatter.curiousconcept.com/ for assistance\n"
  raise SystemExit


DATA = [config['assets']['movies']['saved_data'], 
        config['assets']['series']['saved_data'], 
        config['assets']['documentaries']['saved_data']]

HELP = """\nUsage: 
            python remove_entry.py [type] "<filename>"
            \n[type] : 
            -m, --movie \t\t=> movie
            -s, --series \t\t=> series
            \nExamples: 
            python remove_entry.py -m "Monty Python and the Holy Grail"
            python remove_entry.py --series "Six Feet Under"
            \nNote:
            Use single quotes around title if it contains special characters (such as '!')\n"""


def remove_file(filetype, asset_name):

  if filetype in ['-m', '--movie']:
    filename = DATA[0]
  elif filetype in ['-s', '--series']:
    filename = DATA[1]
  elif filetype in ['-d', '--documentary']:
    filename = DATA[2]
  else:
    print HELP
    return


  if os.path.isfile(filename):
    found = False

    # Read contents of JSON file
    with open(filename, 'r') as saved_asset_list:
      saved_assets = json.load(saved_asset_list)

    # Delete entry
    try:
      for key in saved_assets:
        if saved_assets[key]['title'].lower() == asset_name.lower():
          del saved_assets[key]
          found = True
          break
      if not found:
        print "\nEntry not found: \"%s\" in \"%s\"\n" % (asset_name, filename)
        return
    except KeyError:
      print "\nEntry not found: \"%s\" in \"%s\"\n" % (asset_name, filename)
      return

    # Write contents to JSON file
    with open(filename, 'w+') as asset_feed:
      json.dump(saved_assets, asset_feed, encoding="utf-8")
  
    print "\nEntry deleted: \"%s\" from \"%s\"\n" % (asset_name, filename)
    return

  else:
    print "\nFile not found: \"%s\"\n" % filename
    return


if __name__ == "__main__":
  try:
    if sys.argv[1] in ["-h", "--help", "--h", " "]:
      print HELP
    else:
      remove_file(sys.argv[1], normalize("NFC", sys.argv[2].decode('UTF-8')))
  except IndexError:
    print HELP
