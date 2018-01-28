from   __future__ import unicode_literals
import datetime
import json
import os
import sys
import pymediainfo
import pdb

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.helpers as helpers
import src.retriever

# Commit 674ff8a17c3b4fcae8ae508200165bb7e953e8cc added a 'list of episodes'
# to the series details
# This is only retreived once a new file is added, and often new episodes are
# continually added

# TODO: this should not be a backfill script run periodically. The worker class
# should ensure this is computed on every run

conf = helpers.verify_config_file()
base_file_path = conf['assets']['series']['location']
exclude = conf['exclude_files']

# Import data file with all saved entries
with open('_data/series_data.json') as series_details:
  series = json.load(series_details)

item_count = 0
skipped = []

print "Script started : {}\n".format(datetime.datetime.now())

for title in series:

  indexed_episodes = series[title].get("episodes") or []
  episodes_on_disk = helpers.get_nested_directory_contents(
    "{}/{}".format(base_file_path, title).replace('//', '/')
  )

  if indexed_episodes and not episodes_on_disk:
    print "Warning: Skipping {} as it exists in the index but not on disk".format(title)
    continue

  if indexed_episodes != episodes_on_disk:
    eps_on_disk = len(sum(episodes_on_disk, []) or [])
    eps_in_json = len(sum(indexed_episodes, []) or [])
    episode_delta = eps_on_disk - eps_in_json

    print "Adding {} episodes to {}".format(episode_delta, title)
    series[title]['episodes'] = episodes_on_disk

# Results will be stored in tmp-file and not overwrite _data/series_data.json
# Verify its integrity and then the suggested manual steps are:
#   mv _data/series_data.json _data/series_data-backup.json
#   mv tmp-file-series _data/series_data.json
with open('tmp-file-series', 'w+') as tmp:
  json.dump(series, tmp, encoding="utf8", indent=4)


print "\nScript completed : {}".format(datetime.datetime.now())
print "Total Series Processed {}".format(len(series))
