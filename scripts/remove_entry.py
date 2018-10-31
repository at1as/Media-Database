#!/usr/bin/env python
# -*- coding: utf8 -*-

# Remove saved entries from saved json repositories
# Useful for entries that have been tagged incorrectly


import os
import sys
import json
from unicodedata import normalize


def relative_path(file_path):
  # Get path relative to this file
  current_dir = os.path.dirname(__file__)
  return os.path.join(current_dir, file_path)


# Import Environment Configuration
try:
  with open(relative_path('../conf.json')) as config_json:
    config = json.load(config_json)
except Exception as e:
  print("\nInvalid JSON body in conf.json\nSee: http://jsonformatter.curiousconcept.com/ for assistance %s\n" % e)
  raise SystemExit


DATA = [config['assets']['movies']['saved_data'], 
        config['assets']['series']['saved_data']]

HELP = """\nUsage: 
            python remove_entry.py [type] "<filename>" [year]
            \n[type] : 
            -m, --movie \t\t=> movie
            -s, --series \t\t=> series
            \n[year] :
            - four digit year
            - The [year] field is optional. If not passed, first matching title will be deleted
            \nExamples: 
            python remove_entry.py -m "Monty Python and the Holy Grail"
            python remove_entry.py --series "Six Feet Under" 2001
            \nNote:
            - Use single quotes around title if it contains special characters (such as '!')
            - The [year] field is optional. If not passed, first matching title will be deleted\n"""


def remove_file(filetype, asset_name, year):

  if filetype in ['-m', '--movie']:
    filename = DATA[0]
  elif filetype in ['-s', '--series']:
    filename = DATA[1]
  else:
    print(HELP)
    return


  if os.path.isfile(relative_path('../' + filename)):
    found = False

    # Read contents of JSON file
    with open(relative_path('../' + filename), 'r') as saved_asset_list:
      saved_assets = json.load(saved_asset_list)

    # Delete entry
    try:
      for key in saved_assets:
        if saved_assets[key]['title'].lower().replace(':', '').strip() == asset_name.lower().replace(':', '').strip():

          # Find entry matching year if arg is passed, else delete first matching title found
          if year is None or (saved_assets[key]['year'] == year):
            del saved_assets[key]
            found = True
            break

      if not found:
        year_arg = year or "any year"
        print("\nEntry not found: \"%s\" for %s in \"%s\"\n" % (asset_name, year or "any year", filename))
        return
    except KeyError:
      print("\nEntry not found: \"%s\" in \"%s\"\n" % (asset_name, filename))
      return

    # Write contents to JSON file
    with open(relative_path('../' + filename), 'w+') as asset_feed:
      json.dump(saved_assets, asset_feed, encoding="utf-8", indent=4)
  
    print("\nEntry deleted: \"%s\" from \"%s\"\n" % (asset_name, filename))
    return

  else:
    print("\nFile not found: \"%s\"\n" % filename)
    return


if __name__ == "__main__":
  try:
    if sys.argv[1] in ["-h", "--help", "--h", " "]:
      print(HELP)
    else:
      if len(sys.argv) == 4:
        remove_file(sys.argv[1], normalize("NFC", sys.argv[2].decode('UTF-8')), sys.argv[3])
      else:
        # Year arg was passed
        remove_file(sys.argv[1], normalize("NFC", sys.argv[2].decode('UTF-8')), None)
  except IndexError:
    print(HELP)
