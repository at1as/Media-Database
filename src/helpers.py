import json
from message import Message
import os
from pymediainfo import MediaInfo
import pdb

# Change User Agent header from Requests to Mozilla for requests made to IMDB
HEADERS = {
  "User-Agent":      "Mozilla/5.0",
  "Accept-Language": "en-US,en;q=0.8"
}


def relative_path(file_path):
  # Get path relative to this file location
  current_dir = os.path.dirname(__file__)
  return os.path.join(current_dir, file_path)


def path_of_depth(file_path, depth):
  # "/Volumes/Drive/Folder/Subfolder/File.mkv" -> "Subfolder/File.mkv"
  if file_path is None:
    return

  return "/".join(file_path.split('/')[-depth:])


def verify_config_file():
  # Import Input Environment Configuration and Validation
  try:
    config = get_config_file()

    if config["include_extensions"] == []:
      Message.warn("No extensions specified in include_extensions in conf.json. Will not currently scrape for any filetypes")
    
    if config["base_url"] != "http://www.imdb.com" or config["search_path"] != "/find?q=" or config["url_end"] != "&s=all":
      Message.warn("base_url, search_path or url_end have been changed from their defaults in conf.json. Proceed at your own risk")

    for asset_type in config["assets"]:
      if config["assets"][asset_type]["saved_data"] == "":
        Message.error("Error: Please specify a path for the assets.{}.saved_data repository in conf.json".format(asset_type))
        raise SystemExit

      if not type(config["assets"][asset_type]["max_assets"]) is int or config["assets"][asset_type]["max_assets"] < 0:
        Message.error("Please specify a valid integer for assets.{}.max_quantity repository in conf.json".format(asset_type))
        raise SystemExit
      
      if config["assets"][asset_type]["index_asset"] and config["assets"][asset_type]["location"] == "":
        Message.error("\"{}\" is set to index files, but path to directory is not specified in conf.json\n".format(asset_type))
        raise SystemExit

  except Exception as e:
    Message.error("Invalid JSON body in conf.json.\nSee: http://jsonformatter.curiousconcept.com/ for assistance\n")
    raise SystemExit

  return config


def get_config_file():
  # Read configuration file. Raises exception if not found
  with open(relative_path('../conf.json')) as config_json:
    return json.load(config_json)


def get_filepath_from_dir(filepath):
  # Given the path to a directory, try to find the video file in the subdirectory
  # - Do not descend further into children directories
  # - function does not verify file is media, but takes a best guess from filtering rules below
  if not filepath:
    return
  
  if os.path.isfile(filepath):
    return filepath
  
  if os.path.isdir(filepath):
    files = os.listdir(filepath)
    
    # Create absolute path to file, filter out deeper sub directories
    files = map(lambda x: "{}/{}".format(filepath.rstrip("/"), x), files)
    files = filter(lambda x: not os.path.isdir(x), files)

    # Remove non-video extensions. Assume all valid video extensions are 3 or 4 digits
    files = filter(lambda x: x.lower().split(".")[-1] not in ["srt", "txt", "md", "nfo", "idx", "sub", "ds_store"], files)
    files = filter(lambda x: len(x.split(".")[-1]) in [3, 4], files)

    # No valid files after filtering
    if not files:
      return

    # Try to directly get a video file by a list of common extensions
    # Otherwise, we'll simply try with first remaining item in the list
    # TODO : Could return all remaining paths to pass to mediainfo to see if we can find the video file
    video_files = filter(lambda x: x.lower().split(".")[-1] in ["avi", "mp4", "mpeg", "mpg", "mkv", "wmv", "flv"], files)
    if video_files:
      return video_files[0]
    else:
      return files[0]


def video_dimensions(filepath):
  # Get media info from file
  if not filepath:
    return
  
  # Get media file resolution
  media_info = MediaInfo.parse(filepath)
  
  try:
    video_track = [t for t in media_info.tracks if t.track_type == 'Video'][0]
  except:
    return

  if video_track.width == 7680:
    return "8K"
  elif video_track.width == 3480:
    return "4K"
  elif video_track.width == 1920:
    return "1080p"
  elif video_track.width == 1280:
    return "720p"
  elif video_track.width < 1280:
    return "SD"
  else:
    return "{}x{}".format(video_track.width, video_track.height)

