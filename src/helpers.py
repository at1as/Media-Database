from message import Message
import json
import pdb

# Change User Agent header from Requests to Mozilla for requests made to IMDB
HEADERS = {
  "User-Agent":      "Mozilla/5.0",
  "Accept-Language": "en-US,en;q=0.8"
}


def verify_config_file():
  # Import Input Environment Configuration and Validation
  try:
    config = get_config_file()

    if config["include_extensions"] == []:
      Message.warn("No extensions specified in include_extensions in conf.json. Will not currently scrape for any filetypes")
    
    if config["base_url"] != "http://www.imdb.com" or config["search_path"] != "/find?q=" or config["url_end"] != "&s=all":
      Message.warn("base_url, search_path and url_end have been changed from their defaults in conf.json. Proceed at your own risk")

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

  except:
    Message.error("Invalid JSON body in conf.json.\nSee: http://jsonformatter.curiousconcept.com/ for assistance\n")
    raise SystemExit

  return config


def get_config_file():
  with open('conf.json') as config_json:
    config = json.load(config_json)

  return config
