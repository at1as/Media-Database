import json
import os

"""
  Will create symlink needed to stream media over apache to other devices on the network
  The first step is manual, and requires your Apache directory to be symlinked to this repository
  
  - Ex. "ln -s /Library/WebServer/Documents/IMDB-Scrape ~/GitRepos/IMDB-Scrape"

  The script will then symlink the Movies asset location to IMDB-Scrape so that media can be streamed
  
  n.b. Will currently only work with Safari browser and H264 content
"""

# Read JSON file with path to asset location
try:
  with open('conf.json') as config_json:
    config = json.load(config_json)
except Exception as e:
  print 'Invalid JSON in config.json : %s' %(e)
  raise SystemExit

# Symlinking only movies because directories are not currently descended
# Series will always be contained within directories
destination = config["assets"]["movies"]["location"]

# Symbolic link command for *nix systems
command = "ln -s %s ./Movies" %(destination)

try:
  os.system(command)
except Exception as e:
  print "Could not execute symlink command : %s" %(e)

