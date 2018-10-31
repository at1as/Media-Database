
from datetime import datetime
from . import helpers
import jinja2

class SiteGenerator(object):
  def __init__(self):
    pass


  @staticmethod
  def build_site(saved_movies, saved_series):
    """
      Generate static HTML files
    """
    movie_location = helpers.get_movie_location()

    num_movies = len(saved_movies)
    num_series = len(saved_series)

    # Output Environment for static html generation
    env            = jinja2.Environment(loader=jinja2.FileSystemLoader(["./_templates"]))
    movie_index    = env.get_template("index.html")
    series_index   = env.get_template("series.html")
    about          = env.get_template("about.html")
    movie_details  = env.get_template("movie_details.html")
    series_details = env.get_template("series_details.html")

    # List Pages
    SiteGenerator.build_movies_index_page(movie_index, saved_movies, num_series)
    SiteGenerator.build_series_index_page(series_index, saved_series, num_movies)

    # Instance Pages
    SiteGenerator.build_about_page(about, num_movies, num_series)
    SiteGenerator.build_movie_pages(saved_movies, movie_details, num_movies, num_series, movie_location)
    SiteGenerator.build_series_pages(saved_series, series_details, num_movies, num_series)


  @staticmethod
  def build_movies_index_page(movies_index, saved_movies, num_series):
    """ Movie Index Page """
    movies_page = movies_index.render(
      movie_list = saved_movies,
      number_of_series = num_series
    )

    f = open("_output/index.html", "w")
    f.write(movies_page.encode('utf-8'))
    f.close


  @staticmethod
  def build_series_index_page(series_index, saved_series, num_movies):
    """ TV Series Index Page """
    series_page = series_index.render(
      series_list = saved_series,
      number_of_movies = num_movies
    )

    f = open("_output/series.html", "w")
    f.write(series_page.encode('utf-8'))
    f.close


  @staticmethod
  def build_about_page(about, num_movies, num_series):
    """ About Page """
    about_page = about.render(
      number_of_movies = num_movies,
      number_of_series = num_series,
      time = str(datetime.now())
    )

    f = open("_output/about.html", "w")
    f.write(about_page.encode('utf-8'))
    f.close


  @staticmethod
  def build_movie_pages(saved_movies, movie_details, num_movies, num_series, movie_location):
    """ Individual Movie Pages, one for each movie """
    for item in saved_movies:
      output_dir = "_output/movies/%s(%s).html" %(saved_movies[item]['title'].replace('/', ''), saved_movies[item]['year'])
      movie_page = movie_details.render(
        number_of_movies = num_movies,
        movie = saved_movies[item],
        number_of_series = num_series,
        location = movie_location
      )

      f = open(output_dir, "w")
      f.write(movie_page.encode('utf-8'))
      f.close


  @staticmethod
  def build_series_pages(saved_series, series_details, num_movies, num_series):
    """ Individual Series Pages, one for each movie """
    for item in saved_series:
      output_dir = "_output/series/%s(%s).html" %(saved_series[item]['title'].replace('/', ''), saved_series[item]['year'][0:4])
      series_page = series_details.render(
        number_of_series = num_series,
        series = saved_series[item],
        number_of_movies = num_movies
      )

      f = open(output_dir, "w")
      f.write(series_page.encode('utf-8'))
      f.close
