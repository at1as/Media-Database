
import datetime
import json
import os
import sys
import pymediainfo
import pdb

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.helpers as helpers
import src.worker

# Commit 872bdaab9ae92c5f40b3f8d04abbdd7bd56c6982 added 'file_attributes' and `media`
# objects within each movie. This script modifies the existing schema in place
# to populate these objects if not present

conf = helpers.verify_config_file()
location = conf['assets']['movies']['location']
exclude  = conf['exclude_files']

# Import data file with all saved entries
with open('_data/movie_data.json') as movie_details:
  movies = json.load(movie_details)

item_count = 0
skipped = []
all_files = os.listdir(location)

print("Script started : {}\n".format(datetime.datetime.now()))

for file in movies:
  item_count += 1

  # Skip hidden files or files slated to
  if file.startswith('.') or file in exclude:
    print("Skipping Excluded file {}".format(file))
    skipped.append(file)
    continue

  try:
    if movies[file].get('file_metadata'):
      continue

    top_level_dir = movies[file]['filename']

    if movies[file]['extension']:
      top_level_dir = "{}.{}".format(top_level_dir, movies[file]['extension'])

    full_filepath = helpers.get_filepath_from_dir("{}{}".format(location, top_level_dir))

    #pdb.set_trace()
    partial_filepath = full_filepath.split(conf["assets"]["movies"]["location"])[-1]

    media_metadata = helpers.video_media_details(full_filepath)
    movies[file]['media'] = media_metadata

    try:    del movies[file]['format']
    except: pass
    try:    del movies[file]['width']
    except: pass
    try:    del movies[file]['height']
    except: pass
    try:    del movies[file]['bit_depth']
    except: pass
    try:    del movies[file]['bit_rate']
    except: pass
    try:    del movies[file]['subtitles']
    except: pass

    movies[file]['file_metadata'] = {}
    movies[file]['file_metadata']['filename']  = movies[file]['filename']
    movies[file]['file_metadata']['extension'] = movies[file]['extension']
    movies[file]['file_metadata']['relative_path'] = partial_filepath
    movies[file]['file_metadata']['absolute_path'] = full_filepath

    try:    del movies[file]['filename']
    except: pass
    try:    del movies[file]['extension']
    except: pass
    try:    del movies[file]['relative_path']
    except: pass
    try:    del movies[file]['absolute_path']
    except: pass

  except Exception as e:
    skipped.append(file)
    print("{}: Skipping file {}. Not found ({})".format(item_count, file, e))
    continue


# Results will be stored in tmp-file and not overwrite _data/movie_data.json
# Verify its integrity and then the suggested manual steps are:
#   mv _data/movie_data.json _data/movie_data-backup.json
#   mv tmp-file _data/movie_data.json
with open('tmp-file', 'w+') as tmp:
  json.dump(movies, tmp, encoding="utf8", indent=4)


# Ensure extension count is accurate
print("\nScript completed : {}".format(datetime.datetime.now()))

print("Skip List {}".format(skipped))
print("Total Files {}".format(item_count))
