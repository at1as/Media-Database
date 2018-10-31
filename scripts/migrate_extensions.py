  
import json
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.helpers as helpers

# Migration script for existing movie_data.json file which does not contain file extensions
# For schema change in commit 853c15fc0722d7db38dfdfe824acc9d90ac411c7 onwards
# Script will not descend into folders, so files stored in folders (series, movies with separate subs, etc) will be stored
# in movie_data.json with extension: null, all other files should have a key for filename and another for extension

# Import configuration file with location of assets
conf = helpers.verify_config_file()
location = conf['assets']['movies']['location']
exclude = conf['exclude_files']

# Import data file with all saved entries
with open('_data/movie_data.json') as movie_details:
  movies = json.load(movie_details)

item_count = 0
skipped = []
all_files = os.listdir(location)
extension_count = {}

for file in all_files:
  item_count += 1

  # Skip hidden files or files slated to 
  if file.startswith('.') or file in exclude:
    print("Skipping Excluded file {}".format(file))
    skipped.append(file)
    continue

  try:
    # If folder (assuming naming conventions of <title (YYYY)> is followed
    if file.endswith(')'):
      movies[file]['extension'] = None

      if 'folder' in extension_count:
        extension_count['folder'] += 1
      else:
        extension_count['folder'] = 1 
    
    else:
      filename, extension = file.rsplit('.', 1)
      movies[filename]['extension'] = extension

      if extension in extension_count:
        extension_count[extension] += 1
      else:
        extension_count[extension] = 1
  except:
    skipped.append(file)
    print("Skipping file {}. Not found".format(file))
    continue

# Results will be stored in tmp-file and not overwrite _data/movie_data.json
# Verify its integrity and then the suggested manual steps are:
#   mv _data/movie_data.json _data/movie_data-backup.json
#   mv tmp-file_extension-migration _data/movie_data.json
with open('tmp-file_extension-migration', 'w+') as tmp:
  json.dump(movies, tmp, encoding="utf8")


# Ensure extension count is accurate
print(extension_count)
print("Skip List {}".format(skipped))
print("Total Files {}".format(item_count))
