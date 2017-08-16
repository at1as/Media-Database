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

# Commit 9396a0a729d8bbcd1bd559881408cbdeda82f64a added a 'resolution' field to the movie data
# This is only retreived once a new file is added 

conf = helpers.verify_config_file()
location = conf['assets']['movies']['location']
exclude = conf['exclude_files']

# Import data file with all saved entries
with open('_data/movie_data.json') as movie_details:
  movies = json.load(movie_details)

item_count = 0
skipped = []
all_files = os.listdir(location)

print "Script started : {}\n".format(datetime.datetime.now())

for file in movies:
  item_count += 1
  
  # Skip hidden files or files slated to 
  if file.startswith('.') or file in exclude:
    print "Skipping Excluded file {}".format(file)
    skipped.append(file)
    continue

  try:
    if movies[file].get('resolution') and movies[file].get('relative_path'):
      continue
    
    top_level_dir = movies[file]['filename']
    
    if movies[file]['extension']:
      top_level_dir = "{}.{}".format(top_level_dir, movies[file]['extension'])

    filepath = helpers.get_filepath_from_dir("{}{}".format(location, top_level_dir))
    resolution = helpers.video_dimensions(filepath)

    movies[file]['resolution'] = resolution
    movies[file]['relative_path'] = filepath

  except Exception as e:
    skipped.append(file)
    print "Skipping file {}. Not found ({})".format(file, e)
    continue

  if resolution is None or filepath is None:
    print "File : {} had resolution {} and path {}".format(file, resolution, filepath)


# Results will be stored in tmp-file and not overwrite _data/movie_data.json
# Verify its integrity and then the suggested manual steps are:
#   mv _data/movie_data.json _data/movie_data-backup.json
#   mv tmp-file _data/movie_data.json
with open('tmp-file', 'w+') as tmp:
  json.dump(movies, tmp, encoding="utf8", indent=4)


# Ensure extension count is accurate
print "\nScript completed : {}".format(datetime.datetime.now())

print "Skip List {}".format(skipped)
print "Total Files {}".format(item_count)

