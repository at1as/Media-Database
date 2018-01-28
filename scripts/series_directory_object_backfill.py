from   __future__ import unicode_literals
import datetime
import json
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Commit e6bb9b7 changed the flat structure of of 'filename' and 'extension'
# to use a nested `directory` object. This script modifies existing entries in
# in series_data.json to use the new schema

with open('_data/series_data.json') as series_details:
  series_list = json.load(series_details)

for series in series_list:
  directory = {
    'name': series_list[series].get('filename'),
    'absolute_path': series_list[series].get('absolute_path'),
    'relative_path': series_list[series].get('relative_path')
  }

  series_list[series]['directory'] = directory

  try:    del series_list[series]['relative_path']
  except: pass
  try:    del series_list[series]['filename']
  except: pass
  try:    del series_list[series]['extension']
  except: pass


# Results will be stored in tmp-file and not overwrite _data/movie_data.json
# Verify its integrity and then the suggested manual steps are:
#   mv _data/movie_data.json _data/movie_data-backup.json
#   mv tmp-file _data/movie_data.json
with open('tmp-series-schema-change', 'w+') as tmp:
  json.dump(series_list, tmp, encoding="utf8", indent=4)


# Ensure extension count is accurate
print "\nScript completed : {}".format(datetime.datetime.now())
