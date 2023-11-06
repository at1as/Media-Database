#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
  name='movie_database',
  description='Local Media database sourced from IMDB',
  author='Jason Willems',
  author_email='hello@jasonwillems.com',
  url='https://github.com/at1as/IMDB-Scrape',
  install_requires=[
    'certifi==2017.7.27.1'
    'chardet==3.0.4'
    'cinemagoer==2023.5.1'
    'idna==2.5'
    'Jinja2==2.9.6'
    'lxml==3.8.0'
    'MarkupSafe==1.0'
    'pymediainfo==2.1.9'
    'requests==2.18.3'
    'urllib3==1.22'
  ],
)
