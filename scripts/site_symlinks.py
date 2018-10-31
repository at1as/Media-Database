import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.helpers as helpers

"""
  Will create symlink needed to stream media over apache to other devices on the network
  The first step is manual, and requires your Apache directory to be symlinked to this repository
  
  - Ex. "ln -s /Library/WebServer/Documents/IMDB-Scrape ~/GitRepos/IMDB-Scrape"

  The script will then symlink the Movies asset location to IMDB-Scrape so that media can be streamed
  
  n.b. Will currently only work with Safari browser and H264 content

  run me as `python scripts/site_symlinks.py` so the relative path of ./Movies below is correctly built
"""

# Read JSON file with path to asset location
config = helpers.verify_config_file()

# Symlinking only movies because directories are not currently descended
# Series will always be contained within directories
destination = config["assets"]["movies"]["location"]

# Symbolic link command for *nix systems
command = "ln -s {} ./Movies".format(destination)

try:
  os.system(command)
except Exception as e:
  print("Could not execute symlink command : {}".format(e))

