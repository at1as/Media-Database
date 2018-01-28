import requests
from helpers import HEADERS
import shutil

class Image(object):
  def __init__(self):
    pass

  @staticmethod
  def fetch_remote_image(url):
    """ Fetch remote image, return raw image or return a null response """
    try:
      img = requests.get(url, headers=HEADERS, stream=True)

      if img.status_code == 200:
        return img.raw
    except:
      return

  @staticmethod
  def save_remote_image(url, name, mediatype):
    """
      Write image to directory if image was found at URL
      (Occasionally IMDB has no image for a movie)
    """
    image = Image.fetch_remote_image(url)

    if not image:
      return

    if mediatype == "movie":
      media_dir = "movies"
    elif mediatype == "series":
      media_dir = "series"

    try:
      # TODO use relative_path helper function
      with open('_output/images/' + media_dir + '/' + name + '.png', 'wb') as f:
        img.decode_content = True
        shutil.copyfileobj(img, f)
    except:
      pass
