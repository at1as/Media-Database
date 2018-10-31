from abc import ABCMeta, abstractmethod

class BaseScraper(object, metaclass=ABCMeta):
  def __init__(self):
    pass

  @abstractmethod
  def construct_search_url(self, title):
    raise NotImplementedError
  
  @abstractmethod
  def get_title(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_alternative_title(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_description(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_director(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_rating(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_genres(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_votes(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_running_time(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_content_rating(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_stars(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_languages(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_image_url(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_movie_year(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_awards(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_series_year(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_creator(self, xml_doc):
    raise NotImplementedError
  
  @abstractmethod
  def get_movie_details(self, movie, mediatype, movie_url):
    raise NotImplementedError
  
  @abstractmethod
  def get_series_details(self, eries, mediatype, series_url):
    raise NotImplementedError

