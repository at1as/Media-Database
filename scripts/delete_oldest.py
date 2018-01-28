from   __future__ import unicode_literals
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Delete the oldest `n` entries
try:
  limit = int(sys.argv[1]) or 1
except:
  print "Usage: python delte_oldest.py [n]  -> Where n is an integer of items to be deleted"
  sys.exit()

# Import data file with all saved entries
with open('_data/movie_data.json') as movie_details:
  movies = json.load(movie_details)

# Sort by date info was retreived
oldest_entries = sorted(movies.iteritems(), key=lambda (title, payload): payload['info_retrieved'])[0:limit]
titles = [x[0] for x in oldest_entries]

# Delete the oldest entries
print "Deleting the following titles: {}".format(titles)
for title in titles:
  del movies[title]

# Write modifiedcontents to JSON file
# TODO: Move this from temp file to _data/movies
with open('temp-deleted', 'w+') as asset_feed:
  json.dump(movies, asset_feed, encoding="utf-8", indent=4)
