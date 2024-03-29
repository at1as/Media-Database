#!/usr/bin/env python
# -*- coding: utf8 -*-


from datetime import datetime
from .site_generator import SiteGenerator
from . import helpers
from .helpers import video_media_details, get_filepath_from_dir, path_of_depth
from .image import Image
import json
from .message import Message
import os
from . import scraper


class Worker():
  def __init__(self):
    self.config = helpers.verify_config_file()
    self.series_scraper = None
    self.movie_scraper = None

  def start(self, dry_run=False):
    script_started = datetime.now()

    if dry_run:
      saved_movies  = self.write_scraped_data("movies", [])
      saved_series  = self.write_scraped_data("series", [])
      saved_standup = self.write_scraped_data("standup", [])
      SiteGenerator.build_site(saved_movies, saved_series, saved_standup)
    else:
      added_movies = self.fetch_new_files("movies", "movie")
      added_series = self.fetch_new_files("series", "series")
      added_standup = self.fetch_new_files("standup", "standup")
      saved_movies = self.write_scraped_data("movies", added_movies)
      saved_series = self.write_scraped_data("series", added_series)
      saved_standup = self.write_scraped_data("standup", added_standup)

      SiteGenerator.build_site(saved_movies, saved_series, saved_standup)

    time_taken = (datetime.now() - script_started).seconds
    Message.success("Script completed after {} seconds\n".format(time_taken))


  def fetch_new_files(self, base_path, mediatype):
    """
      - Create empty datafiles if not present
      - Return list of newly added file data
    """

    if not os.path.isfile(self.config['assets'][base_path]['saved_data']):
      with open(self.config['assets'][base_path]['saved_data'], 'w+') as item_feed:
        json.dump({}, item_feed)

    if self.config['assets'][base_path]['index_asset']:
      return self.compile_file_list(
        self.config['assets'][base_path]['location'],
        self.config['assets'][base_path]['saved_data'],
        mediatype
      )

    return []


  def get_file_list(self, path, repo, mediatype):
    """
      return list of files, for files whose information has not yet been scraped:
        [
          { 'name': ..., 'extension': ..., 'full_path': ..., 'relative_path': ... },
          { 'name': ..., 'extension': ..., 'full_path': ..., 'relative_path': ... },
          ...
        ]
    """
    asset_type = "movies" if mediatype == "movie" else mediatype

    file_list = self.verify_file_list(asset_type, path)
    filtered_file_list = []

    for file in file_list:

      # If the extension is in include_extension, or file is a folder not preceded by '_'
      if (((os.path.isfile(path + file) and file.split(".")[-1:][0].lower() in self.config["include_extensions"]) or
           (os.path.isdir(path + file) and file[0] != "_")) and
           file not in self.config["exclude_files"]):

        # Strip extension from file
        if os.path.isfile(path + file):
          file_details = {
            'name':          file.rsplit(".", 1)[0],
            'extension':     file.rsplit('.', 1)[1],
            'full_path':     path + file,
            'relative_path': file
          }

        else:
          nested_filepath = get_filepath_from_dir(path + file)
          extension = nested_filepath.split('.')[-1] if nested_filepath else None
          file_details = {
            'name':          file,
            'extension':     extension,
            'full_path':     nested_filepath,
            'relative_path': path_of_depth(nested_filepath, 2)
          }

        # Drop prepending "._" from files on external drives
        if file_details['name'][0:2] == "._":
          file_details['name'] = file_details['name'][2:]

        # Add the file if it is not already in
        with open(repo, 'r') as saved_file_list:
          saved_files = json.load(saved_file_list)

          # Do not repeat scrape for already acquired title
          if file_details['name'] not in saved_files:
            print(("Now adding: %s : %s" %(path, file_details['name'])))
            filtered_file_list.append(file_details)

    return filtered_file_list


  def verify_file_list(self, asset_type, path) -> list[str]:
    """
      Return list of files from directoy, or exit if path is invalid_results
    """
    try:
      # Enforce per asset type limit
      if self.config["assets"][asset_type]["max_assets"] <= 0:
        return os.listdir(path)
      else:
        print(("Fetching up to " + str(self.config["assets"][asset_type]["max_assets"]) + " files for asset type: " + asset_type))
        return os.listdir(path)[0:self.config["assets"][asset_type]["max_assets"]]

    except OSError:
      Message.error(
        "Path \"{}\" not found. Specify a valid path in conf.json and ensure all directories on this path exist.\n".format(path)
      )
      raise SystemExit

  """
  def get_title_url(self, asset, mediatype):
    "" Return the complete URL corresponding to particular title ""

    if mediatype == "movie":
      page_url = self.movie_scraper.get_movie_page_url(asset)
    elif mediatype == "series":
      page_url = self.series_scraper.get_series_page_url(asset)

    if page_url is None:
      print(Message.warn("\"{}\" not found. Skipping.".format(asset)))

    return page_url
  """

  def compile_file_list(self, path, repo, mediatype):
    """
    path          -> top level directory starting from asset directory in conf file
      ex. DoctorWho/

    relative_path -> complete file path starting at "/"
        ex. /Volumes/Media/Series/DoctorWho/

      Returns list of
    """

    file_attributes_list = []
    for file_details in self.get_file_list(path, repo, mediatype):

      if mediatype == "movie":

        movie_id_override = self.config["file_override"].get(file_details["relative_path"], None)
        if movie_id_override:
          print("Initializing movie scraper for {} with override id: {}".format(file_details["name"], movie_id_override))
          self.movie_scraper = scraper.IMDBV2(file_details["name"], movie_id_override)
        else:
          self.movie_scraper = scraper.IMDBV2(file_details["name"])

        file_attributes = self.movie_scraper.get_movie_details(file_details, None)
        file_attributes['file_metadata'] = {}
        file_attributes['file_metadata']['filename']  = file_details['name']
        file_attributes['file_metadata']['extension'] = file_details['extension']
        file_attributes['file_metadata']['absolute_path'] = file_details['full_path']
        file_attributes['file_metadata']['relative_path'] = file_details['relative_path']

      elif mediatype == "series":
        self.series_scraper = scraper.IMDBV2(file_details["name"])
        file_attributes = self.series_scraper.get_series_details(file_details, None)
        file_attributes['directory'] = {}
        file_attributes['directory']['name'] = file_details['name']
        file_attributes['directory']['absolute_path'] = file_details['full_path']
        file_attributes['directory']['relative_path'] = file_details['relative_path']

      elif mediatype == "standup":
        self.movie_scraper = scraper.IMDBV2(file_details["name"])

        file_attributes = self.movie_scraper.get_standup_details(file_details, None)
        file_attributes['file_metadata'] = {}
        file_attributes['file_metadata']['filename'] = file_details['name']
        file_attributes['file_metadata']['extension'] = file_details['extension']
        file_attributes['file_metadata']['absolute_path'] = file_details['full_path']
        file_attributes['file_metadata']['relative_path'] = file_details['relative_path']

      if file_attributes != None:
        if mediatype == "movie" or mediatype == "standup":
          file_attributes['media'] = video_media_details(file_details['full_path'])

        elif mediatype == "series":
          file_attributes['episodes'] = helpers.get_nested_directory_contents(
            "{}/{}".format(path, file_details['name']).replace('//', '/')
          )

        Image.save_remote_image(
          file_attributes['image_url'],
          file_details['name'],
          mediatype
        )

        file_attributes_list.append(file_attributes)

    return file_attributes_list


  def write_scraped_data(self, base_path, additional_assets):
    """
      Write newly added assets to json file
      Return existing and new assets
      # TODO: this function doesn't belong in this class
    """

    # Import all pre-existing data from JSON file
    # TODO use relative path helper
    print(("Reading current saved info from path: " + self.config['assets'][base_path]['saved_data']))
    with open(self.config['assets'][base_path]['saved_data'], 'r') as asset_feed:
      saved_assets = json.load(asset_feed)

    if additional_assets != []:

      # Add new saved assets to JSON file
      for asset in additional_assets:
        if base_path == "movies" or base_path == "standup":
          saved_assets[asset['file_metadata']['filename']] = asset
        else:
          saved_assets[asset['directory']['name']] = asset

      # Write combined asset contents to JSON file
      # TODO: use relative path helper
      with open(self.config['assets'][base_path]['saved_data'], 'w+') as asset_feed:
        json.dump(saved_assets, asset_feed, indent=4)

    return saved_assets
