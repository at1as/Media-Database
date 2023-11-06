
from collections import OrderedDict
import json
from .message import Message
import os
from pymediainfo import MediaInfo
import re

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

def get_movie_location():
  # TODO: use relative path helper
  try:
    with open('conf.json') as config_json:
      return json.load(config_json)['assets']['movies']['location']
  except:
    return

def verify_config_file():
  # Import Input Environment Configuration and Validation
  try:
    config = get_config_file()

    if config["include_extensions"] == []:
      Message.warn("No extensions specified in include_extensions in conf.json. Will not currently scrape for any filetypes")

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
    files = ["{}/{}".format(filepath.rstrip("/"), x) for x in files]
    files = [x for x in files if not os.path.isdir(x)]

    # Remove non-video extensions. Assume all valid video extensions are 3 or 4 digits
    files = [x for x in files if x.lower().split(".")[-1] not in ["srt", "txt", "md", "nfo", "idx", "sub", "ds_store"]]
    files = [x for x in files if len(x.split(".")[-1]) in [3, 4]]

    # No valid files after filtering
    if not files:
      return

    # Try to directly get a video file by a list of common extensions
    # Otherwise, we'll simply try with first remaining item in the list
    # TODO : Could return all remaining paths to pass to mediainfo to see if we can find the video file
    video_files = [x for x in files if x.lower().split(".")[-1] in ["avi", "mp4", "mpeg", "mpg", "mkv", "wmv", "flv", "m4v"]]
    if video_files:
      return video_files[0]
    else:
      return files[0]


def video_media_details(filepath):
  # Get media video dimensions info from file path
  if not filepath:
    return

  # Get media file resolution
  media_info = MediaInfo.parse(filepath)

  try:
    video_track = [t for t in media_info.tracks if t.track_type == 'Video'][0]
    subtitles = [x for x in list(set([t.language for t in media_info.tracks if t.track_type == 'Text'])) if x!= None]
  except Exception as e:
    return

  file_details = {
    "format":     video_track.format,
    "width":      video_track.width,
    "height":     video_track.height,
    "bit_depth":  "{} bits".format(video_track.bit_depth) if video_track.bit_depth else None,
    "subtitles":  subtitles
  }

  try:
    # In some bizarre cases the bitrate can come back from pymediainfo as '1200000 / 1200000' instead
    # of a single integer. This is coming from mediainfo directly in this format
    file_details["bit_rate"] = "{} kbps".format(video_track.bit_rate / 1000) if video_track.bit_rate else None
  except TypeError:
    file_details["bit_rate"] = "{} kbps".format(int(video_track.bit_rate.split('/')[0]) / 1000)

  if video_track.width == 7680:
    file_details["resolution"] = "8K"

  elif video_track.width == 3480:
    file_details["resolution"] = "4K"

  elif video_track.width in range(1915, 1925):
    file_details["resolution"] = "1080p"

  elif video_track.width in range(1275, 1285):
    file_details["resolution"] = "720p"

  elif video_track.width < 1275:
    file_details["resolution"] = "SD"

  else:
    file_details["resolution"] = "{}x{}".format(video_track.width, video_track.height)

  return file_details


def get_nested_directory_contents(filepath):
  """
  Translate the following directory structure:

  Doctor Who Season 1/
     Doctor Who S01E01.mp4
     Doctor Who S01E02.avi
  Doctor Who Season 2/
    Doctor Who S02E01.m4a
    Doctor Who S02E02.mp4

  To:

     [
        {"Doctor Who S01E01": <file_metadata>, "Doctor Who S01E02": <file_metadata>, ...},
        {"Doctor Who S02E01": <file_metadata>, "Doctor Who S02E02": <file_metadata>, ...}
     ]
  """
  permitted_extensions = verify_config_file()["include_extensions"]

  try:
    nested_directories = [d for d in natural_sort(os.listdir(filepath)) if os.path.isdir("{}/{}".format(filepath, d))]
    directory_contents = []

    for directory in nested_directories:
      file_contents = {}
      files = os.listdir("{}/{}".format(filepath, directory))

      for f in files:
        path_to_item = os.path.join("{}/{}".format(filepath, directory), f)
        if os.path.isfile(path_to_item) and f.split(".")[-1] in permitted_extensions:
          file_contents[f.rsplit(".", 1)[0]] = video_media_details(path_to_item)

      if file_contents:
        directory_contents.append(OrderedDict(sorted(list(file_contents.items()), key=lambda x_y: x_y[0])))

    return directory_contents
  except Exception as e:
    return []


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)
