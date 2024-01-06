
from datetime import datetime
from . import helpers
import jinja2
import re

class SiteGenerator(object):
  def __init__(self):
    pass

  @staticmethod
  def season_filter(episode_name):
    """
      Extract 'S01' from "Doctor Who S01E01.mkv"
    """
    return re.sub(r".*[sS]([0-9]{2})[eE][0-9]{2}.*", "\\1", str(episode_name))

  @staticmethod
  def build_site(saved_movies, saved_series, saved_standup):
    """
      Generate static HTML files
    """
    movie_location = helpers.get_movie_location()

    num_movies = len(saved_movies)
    num_series = len(saved_series)
    num_standup = len(saved_standup)

    # Output Environment for static html generation
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(["./_templates"]))
    env.filters['seasonnumber'] = SiteGenerator.season_filter

    movie_index     = env.get_template("index.html")
    series_index    = env.get_template("series.html")
    standup_index   = env.get_template("standup.html")
    about           = env.get_template("about.html")
    movie_details   = env.get_template("movie_details.html")
    series_details  = env.get_template("series_details.html")
    standup_details = env.get_template("standup_details.html")

    # List Pages
    SiteGenerator.build_movies_index_page(movie_index, saved_movies, num_series, num_standup)
    SiteGenerator.build_series_index_page(series_index, saved_series, num_movies, num_standup)
    SiteGenerator.build_standup_index_page(standup_index, saved_standup, num_series, num_movies)

    # Instance Pages
    SiteGenerator.build_about_page(about, num_movies, num_series, num_standup)
    SiteGenerator.build_movie_pages(saved_movies, movie_details, num_movies, num_series, num_standup, movie_location)
    SiteGenerator.build_series_pages(saved_series, series_details, num_movies, num_series, num_standup)
    SiteGenerator.build_standup_pages(saved_standup, standup_details, num_movies, num_series, num_standup, movie_location)


  @staticmethod
  def build_movies_index_page(movies_index, saved_movies, num_series, num_standup):
    """ Movie Index Page """
    movies_page = movies_index.render(
      movie_list = saved_movies,
      number_of_series = num_series,
      number_of_standup = num_standup
    )

    with open("_output/index.html", "w") as f:
      f.write(movies_page)


  @staticmethod
  def build_series_index_page(series_index, saved_series, num_movies, num_standup):
    """ TV Series Index Page """
    series_page = series_index.render(
      series_list = saved_series,
      number_of_movies = num_movies,
      number_of_standup = num_standup
    )

    with open("_output/series.html", "w") as f:
      f.write(series_page)

  @staticmethod
  def build_standup_index_page(standup_index, saved_standup, num_series, num_movies):
    """ TV Series Index Page """
    standup_page = standup_index.render(
      standup_list = saved_standup,
      number_of_movies = num_movies,
      number_of_series = num_series
    )

    with open("_output/standup.html", "w") as f:
      f.write(standup_page)


  @staticmethod
  def build_about_page(about, num_movies, num_series, num_standup):
    """ About Page """
    about_page = about.render(
      number_of_movies = num_movies,
      number_of_series = num_series,
      number_of_standup = num_standup,
      time = str(datetime.now())
    )

    with open("_output/about.html", "w") as f:
      f.write(about_page)


  @staticmethod
  def build_movie_pages(saved_movies, movie_details, num_movies, num_series, number_of_standup, movie_location):
    """ Individual Movie Pages, one for each movie """
    for item in saved_movies:
      output_dir = "_output/movies/%s(%s).html" %(saved_movies[item]['title'].replace('/', ''), saved_movies[item]['year'])
      movie_page = movie_details.render(
        number_of_movies = num_movies,
        movie = saved_movies[item],
        number_of_series = num_series,
        number_of_standup = number_of_standup,
        location = movie_location
      )

      with open(output_dir, "w") as f:
        f.write(movie_page)


  @staticmethod
  def build_series_pages(saved_series, series_details, num_movies, num_series, num_standup):
    """ Individual Series Pages, one for each movie """
    for item in saved_series:
      output_dir = "_output/series/%s(%s).html" %(saved_series[item]['title'].replace('/', ''), saved_series[item]['year'][0:4])
      series_page = series_details.render(
        number_of_series = num_series,
        series = saved_series[item],
        number_of_movies = num_movies,
        number_of_standup = num_standup
      )

      with open(output_dir, "w") as f:
        f.write(series_page)

  @staticmethod
  def build_standup_pages(saved_standup, standup_details, num_movies, num_series, number_of_standup, standup_location):
    """ Individual Standup Pages, one for each standup """
    for item in saved_standup:
      output_dir = "_output/standup/%s(%s).html" %(saved_standup[item]['title'].replace('/', ''), saved_standup[item]['year'])
      standup_page = standup_details.render(
        standup = saved_standup[item],
        number_of_movies = num_movies,
        number_of_series = num_series,
        number_of_standup = number_of_standup,
        location = standup_location
      )

      with open(output_dir, "w") as f:
        f.write(standup_page)

