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
  REFRESHABLE_MEDIA_TYPES = {
    "movie": "movies",
    "movies": "movies",
    "series": "series",
    "standup": "standup",
  }

  def __init__(self):
    self.config = helpers.verify_config_file()
    self.series_scraper = None
    self.movie_scraper = None

  def asset_has_required_fields(self, asset, mediatype):
    if not isinstance(asset, dict):
      return False

    required = ['title', 'year']
    if mediatype == "series":
      required.append('directory')
    else:
      required.append('file_metadata')

    for field in required:
      value = asset.get(field)
      if value in [None, "", []]:
        return False

    return True

  def start(self, dry_run=False, refresh_media_type=None, refresh_count=0):
    script_started = datetime.now()

    if dry_run:
      saved_movies  = self.write_scraped_data("movies", [])
      saved_series  = self.write_scraped_data("series", [])
      saved_standup = self.write_scraped_data("standup", [])
      SiteGenerator.build_site(saved_movies, saved_series, saved_standup)
    elif refresh_media_type:
      asset_type = self.normalize_refresh_media_type(refresh_media_type)
      count = self.validate_refresh_count(refresh_count)

      added_movies = self.refresh_oldest_entries("movies", "movie", count) if asset_type == "movies" else []
      added_series = self.refresh_oldest_entries("series", "series", count) if asset_type == "series" else []
      added_standup = self.refresh_oldest_entries("standup", "standup", count) if asset_type == "standup" else []

      saved_movies = self.write_scraped_data("movies", added_movies)
      saved_series = self.write_scraped_data("series", added_series)
      saved_standup = self.write_scraped_data("standup", added_standup)

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

  def normalize_refresh_media_type(self, refresh_media_type):
    asset_type = self.REFRESHABLE_MEDIA_TYPES.get(str(refresh_media_type).lower())
    if asset_type is None:
      Message.error(
        "Invalid refresh media type \"{}\". Use one of: movie, series, standup.\n".format(refresh_media_type)
      )
      raise SystemExit

    return asset_type

  def validate_refresh_count(self, refresh_count):
    try:
      count = int(refresh_count)
    except Exception:
      Message.error("Refresh count must be a positive integer.\n")
      raise SystemExit

    if count <= 0:
      Message.error("Refresh count must be a positive integer.\n")
      raise SystemExit

    return count

  def load_saved_assets(self, base_path):
    if not os.path.isfile(self.config['assets'][base_path]['saved_data']):
      return {}

    with open(self.config['assets'][base_path]['saved_data'], 'r') as asset_feed:
      return json.load(asset_feed)

  def asset_storage_key(self, base_path, asset):
    if base_path == "movies" or base_path == "standup":
      return asset['file_metadata']['filename']

    return asset['directory']['name']

  def parse_info_retrieved(self, value):
    if value in [None, ""]:
      return datetime.min

    try:
      return datetime.strptime(value, "%Y-%m-%d")
    except Exception:
      return datetime.min

  def build_path_from_relative(self, base_path, relative_path):
    if not base_path or not relative_path:
      return None

    return os.path.join(base_path, relative_path.lstrip('/'))

  def resolve_refresh_media_path(self, base_path, asset_name, details, mediatype):
    relative_path = details.get('relative_path')
    absolute_path = details.get('absolute_path')
    extension = details.get('extension')

    candidates = []

    if mediatype in ["movie", "standup"]:
      if relative_path:
        candidates.append(self.build_path_from_relative(base_path, relative_path))
      elif extension:
        candidates.append(os.path.join(base_path, "{}.{}".format(asset_name, extension)))

      if absolute_path:
        candidates.append(absolute_path)

      for candidate in candidates:
        if candidate and os.path.exists(candidate):
          return candidate

      return candidates[0] if candidates else absolute_path

    if relative_path:
      relative_candidate = self.build_path_from_relative(base_path, relative_path)
      if relative_candidate:
        candidates.append(relative_candidate)
        candidates.append(os.path.dirname(relative_candidate))

    if asset_name:
      candidates.append(os.path.join(base_path, asset_name))

    if absolute_path:
      candidates.append(absolute_path)
      candidates.append(os.path.dirname(absolute_path) if os.path.isfile(absolute_path) else absolute_path)

    for candidate in candidates:
      if candidate and os.path.exists(candidate):
        return candidate

    if asset_name:
      return os.path.join(base_path, asset_name)

    return absolute_path

  def build_refresh_file_details(self, base_path, asset_name, asset, mediatype):
    details = asset.get('file_metadata') if mediatype in ["movie", "standup"] else asset.get('directory')
    details = details or {}

    if mediatype in ["movie", "standup"]:
      extension = details.get('extension')
      full_path = self.resolve_refresh_media_path(base_path, details.get('filename') or asset_name, details, mediatype)
      relative_path = details.get('relative_path')

      if extension in [None, ""] and isinstance(full_path, str) and "." in full_path:
        extension = full_path.rsplit(".", 1)[1]

      return {
        'name': details.get('filename') or asset_name,
        'extension': extension,
        'full_path': full_path,
        'relative_path': relative_path or asset_name,
      }

    full_path = self.resolve_refresh_media_path(base_path, details.get('name') or asset_name, details, mediatype)
    nested_filepath = get_filepath_from_dir(full_path) if full_path else None

    return {
      'name': details.get('name') or asset_name,
      'extension': nested_filepath.rsplit(".", 1)[1] if nested_filepath and "." in nested_filepath else None,
      'full_path': full_path,
      'relative_path': details.get('relative_path') or details.get('name') or asset_name,
    }

  def get_refresh_candidates(self, base_path, mediatype, count):
    saved_assets = self.load_saved_assets(base_path)
    sorted_assets = sorted(
      saved_assets.items(),
      key=lambda item: (self.parse_info_retrieved(item[1].get('info_retrieved')), item[0].lower())
    )

    refresh_candidates = []

    for asset_name, asset in sorted_assets:
      file_details = self.build_refresh_file_details(
        self.config['assets'][base_path]['location'],
        asset_name,
        asset,
        mediatype
      )

      if file_details['name'] in [None, ""]:
        Message.warn("Skipping {} refresh candidate '{}' due to missing stored name".format(mediatype, asset_name))
        continue

      refresh_candidates.append(file_details)

      if len(refresh_candidates) >= count:
        break

    return refresh_candidates

  def refresh_oldest_entries(self, base_path, mediatype, count):
    refresh_candidates = self.get_refresh_candidates(base_path, mediatype, count)

    if not refresh_candidates:
      Message.warn("No saved {} entries are available to refresh.".format(base_path))
      return []

    Message.success(
      "Refreshing {} oldest {} entr{} based on info_retrieved".format(
        len(refresh_candidates),
        mediatype,
        "y" if len(refresh_candidates) == 1 else "ies"
      )
    )
    return self.scrape_file_details(
      refresh_candidates,
      mediatype,
      self.config['assets'][base_path]['location']
    )

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


  def get_file_list(self, path, repo, mediatype, limit=None):
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
          # For series, use directory name as relative_path if no video file found
          relative_path = path_of_depth(nested_filepath, 2) if nested_filepath else file
          file_details = {
            'name':          file,
            'extension':     extension,
            'full_path':     nested_filepath,
            'relative_path': relative_path
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
            if isinstance(limit, int) and limit > 0 and len(filtered_file_list) >= limit:
              return filtered_file_list

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

    # Determine asset type key for config lookup
    asset_type = "movies" if mediatype == "movie" else mediatype

    # Optionally cap how many NEW items to process via conf: assets.<type>.max_assets_chunk
    max_chunk = self.config["assets"].get(asset_type, {}).get("max_assets_chunk", None)

    # Gather list of new files not yet in saved repo, stopping early if a limit is set
    # If max_chunk is 0, return empty list (no new additions)
    if isinstance(max_chunk, int) and max_chunk == 0:
      new_files = []
    else:
      new_files = self.get_file_list(path, repo, mediatype, max_chunk if isinstance(max_chunk, int) and max_chunk > 0 else None)

    return self.scrape_file_details(new_files, mediatype, path)

  def scrape_file_details(self, file_details_list, mediatype, base_path=None):
    file_attributes_list = []

    for file_details in file_details_list:

      # Select scraper implementation based on config
      imdb_source = self.config.get("imdb_source", "IMDB_SUGGEST")
      print("DEBUG: Using imdb_source='{}' for mediatype='{}'".format(imdb_source, mediatype))

      if mediatype == "movie":
        try:
          movie_id_override = self.config["file_override"].get(file_details["relative_path"], None)
          if movie_id_override:
            print("Initializing movie scraper for {} with override id: {}".format(file_details["name"], movie_id_override))
            self.movie_scraper = scraper.Scraper(imdb_source, file_details["name"], movie_id_override)
          else:
            self.movie_scraper = scraper.Scraper(imdb_source, file_details["name"])

          file_attributes = self.movie_scraper.get_movie_details(file_details, None)
          # Mark provenance
          file_attributes['source_lib'] = imdb_source
          file_attributes['file_metadata'] = {}
          file_attributes['file_metadata']['filename']  = file_details['name']
          file_attributes['file_metadata']['extension'] = file_details['extension']
          file_attributes['file_metadata']['absolute_path'] = file_details['full_path']
          file_attributes['file_metadata']['relative_path'] = file_details['relative_path']
        except Exception as e:
          Message.warn("Skipping movie '{}': {}".format(file_details['name'], e))
          continue

      elif mediatype == "series":
        try:
          print("DEBUG: Looking for series override with relative_path: '{}'".format(file_details["relative_path"]))
          series_id_override = self.config["file_override"].get(file_details["relative_path"], None)
          series_absolute_path = file_details['full_path']

          if series_absolute_path and os.path.isfile(series_absolute_path):
            series_absolute_path = os.path.dirname(series_absolute_path)
          elif not series_absolute_path and base_path:
            series_absolute_path = "{}/{}".format(base_path, file_details['name']).replace('//', '/')

          if series_id_override:
            print("Initializing series scraper for {} with override id: {}".format(file_details["name"], series_id_override))
            self.series_scraper = scraper.Scraper(imdb_source, file_details["name"], series_id_override)
          else:
            self.series_scraper = scraper.Scraper(imdb_source, file_details["name"])
          file_attributes = self.series_scraper.get_series_details(file_details, None)
          file_attributes['source_lib'] = imdb_source
          file_attributes['directory'] = {}
          file_attributes['directory']['name'] = file_details['name']
          file_attributes['directory']['absolute_path'] = series_absolute_path
          file_attributes['directory']['relative_path'] = file_details['relative_path']
        except Exception as e:
          Message.warn("Skipping series '{}': {}".format(file_details['name'], e))
          continue

      elif mediatype == "standup":
        try:
          standup_id_override = self.config["file_override"].get(file_details["relative_path"], None)
          if standup_id_override:
            print("Initializing standup scraper for {} with override id: {}".format(file_details["name"], standup_id_override))
            self.movie_scraper = scraper.Scraper(imdb_source, file_details["name"], standup_id_override)
          else:
            self.movie_scraper = scraper.Scraper(imdb_source, file_details["name"])

          file_attributes = self.movie_scraper.get_standup_details(file_details, None)
          file_attributes['source_lib'] = imdb_source
          file_attributes['file_metadata'] = {}
          file_attributes['file_metadata']['filename'] = file_details['name']
          file_attributes['file_metadata']['extension'] = file_details['extension']
          file_attributes['file_metadata']['absolute_path'] = file_details['full_path']
          file_attributes['file_metadata']['relative_path'] = file_details['relative_path']
        except Exception as e:
          Message.warn("Skipping standup '{}': {}".format(file_details['name'], e))
          continue

      if file_attributes != None:
        if not self.asset_has_required_fields(file_attributes, mediatype):
          Message.warn("Skipping {} '{}' due to incomplete metadata payload".format(mediatype, file_details['name']))
          continue

        if mediatype == "movie" or mediatype == "standup":
          file_attributes['media'] = video_media_details(file_details['full_path'])

        elif mediatype == "series":
          series_path = file_details['full_path']

          if not series_path and base_path:
            series_path = "{}/{}".format(base_path, file_details['name']).replace('//', '/')

          file_attributes['episodes'] = helpers.get_nested_directory_contents(
            series_path
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
    saved_assets = self.load_saved_assets(base_path)

    if additional_assets != []:

      # Add new saved assets to JSON file
      for asset in additional_assets:
        asset_key = self.asset_storage_key(base_path, asset)
        existing_asset = saved_assets.get(asset_key, {})
        merged_asset = dict(existing_asset)
        merged_asset.update(asset)
        saved_assets[asset_key] = merged_asset

      # Write combined asset contents to JSON file
      # TODO: use relative path helper
      with open(self.config['assets'][base_path]['saved_data'], 'w+') as asset_feed:
        json.dump(saved_assets, asset_feed, indent=4)

    return saved_assets
