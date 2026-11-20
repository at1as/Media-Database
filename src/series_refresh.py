import re
from urllib.parse import urlsplit


METADATA_FIELDS = (
  "title", "alternative_title", "year", "description", "creator", "director",
  "stars", "genre", "rating", "votes", "running_time", "languages",
  "content_rating", "awards", "image_url", "trailer_url", "type",
)


def is_missing(value):
  if isinstance(value, str):
    return value.strip().casefold() in {"", "none", "null", "n/a", "unknown"}
  return value in (None, [], {})


def needs_metadata(record, credit_field="creator"):
  return is_missing(record.get(credit_field)) or is_missing(record.get("description"))


def movie_metadata_gaps(record):
  core_fields = ("description", "director", "stars", "genre", "running_time")
  extra_fields = ("languages", "content_rating", "image_url")
  core = sum(is_missing(record.get(field)) for field in core_fields)
  extra = sum(is_missing(record.get(field)) for field in extra_fields)
  extra += sum(valid_stat(field, record.get(field)) is None for field in ("rating", "votes"))
  return core, extra


def imdb_id_from_url(value):
  if not isinstance(value, str):
    return None
  try:
    url = urlsplit(value.strip())
  except ValueError:
    return None
  if url.scheme not in ("http", "https") or url.hostname not in ("imdb.com", "www.imdb.com", "m.imdb.com"):
    return None
  match = re.fullmatch(r"/title/(tt[0-9]+)/?", url.path)
  return match.group(1) if match else None


def valid_stat(field, value):
  if isinstance(value, bool):
    return None
  try:
    number = float(str(value).replace(",", ""))
  except ValueError:
    return None
  if field == "rating":
    return number if 1 <= number <= 10 else None
  return int(number) if number.is_integer() and number > 0 else None


def movie_detail_would_shrink(field, old, new):
  if is_missing(old):
    return False
  if field in ("title", "year", "type"):
    return True
  if isinstance(old, list):
    return not isinstance(new, list) or len(new) < len(old)
  if field in ("description", "content_rating") and isinstance(old, str):
    return not isinstance(new, str) or len(new.strip()) < len(old.strip())
  return False


def merge_metadata(existing, fetched, preserve_movie_details=False):
  """Return an improved same-title record, keeping local and unavailable fields."""
  expected_id = imdb_id_from_url(existing.get("url"))
  if not isinstance(fetched, dict) or not expected_id or imdb_id_from_url(fetched.get("url")) != expected_id:
    return None

  changes = {}
  improved = False
  for field in METADATA_FIELDS:
    old = existing.get(field)
    new = fetched.get(field)
    if is_missing(new) or (preserve_movie_details and (field == "image_url" or movie_detail_would_shrink(field, old, new))):
      continue

    if field in ("rating", "votes"):
      new = valid_stat(field, new)
      if new is not None and new != valid_stat(field, old):
        changes[field] = new
        improved = True
      continue

    if field == "creator" and not is_missing(old):
      if fetched.get("_creator_lookup_failed"):
        continue
      old_creators = [old] if isinstance(old, str) else old
      new_creators = [new] if isinstance(new, str) else new
      new = list(dict.fromkeys(new_creators + old_creators))

    # Keep a fuller saved plot when IMDb returns only its opening excerpt.
    if field == "description" and isinstance(old, str) and isinstance(new, str):
      saved_plot = " ".join(old.split())
      fetched_plot = " ".join(new.split())
      if len(fetched_plot) < len(saved_plot) and saved_plot.startswith(fetched_plot.rstrip("…. ")):
        continue

    # IMDb sometimes supplies only the premiere year for a series.
    if field == "year" and str(old).startswith(str(new) + "-"):
      continue
    # The generic series type must not erase a more specific saved type.
    if field == "type" and new == "tvSeries" and not is_missing(old):
      continue

    if new != old:
      changes[field] = new
      improved = improved or is_missing(old) or (
        isinstance(new, list) and isinstance(old, list) and len(new) > len(old)
      ) or (
        preserve_movie_details and field == "description" and isinstance(old, str) and len(new.strip()) > len(old.strip())
      )

  if not improved:
    return None
  return {**existing, **changes, "url": fetched["url"]}
