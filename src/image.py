import requests
from .helpers import HEADERS
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

class Image(object):
  def __init__(self):
    pass

  @staticmethod
  def fetch_remote_image(url):
    """ Fetch remote image, return raw image or return a null response """
    try:
      img = requests.get(url, headers=HEADERS, stream=True, timeout=15)

      if img.status_code == 200 and img.headers.get("Content-Type", "").startswith("image/"):
        return img.raw
      img.close()
    except:
      pass

  @staticmethod
  def save_remote_image(url, name, mediatype):
    """
      Write image to directory if image was found at URL
      (Occasionally IMDB has no image for a movie)
    """
    img = Image.fetch_remote_image(url)

    if not img:
      return False

    if mediatype == "movie":
      media_dir = "movies"
    elif mediatype == "series":
      media_dir = "series"
    elif mediatype == "standup":
      media_dir = "standup"

    destination = Path("_output", "images", media_dir, name + ".png")
    temporary_path = None
    try:
      with NamedTemporaryFile(dir=destination.parent, delete=False) as f:
        temporary_path = Path(f.name)
        img.decode_content = True
        shutil.copyfileobj(img, f)
        if not f.tell():
          return False
      mode = destination.stat().st_mode & 0o777 if destination.exists() else 0o644
      temporary_path.chmod(mode)
      temporary_path.replace(destination)
      return True
    except (OSError, ValueError):
      return False
    finally:
      img.close()
      if temporary_path is not None:
        temporary_path.unlink(missing_ok=True)
