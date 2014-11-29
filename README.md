# IMDB-Scrape

Gathers information about movies stored in a local directory and compiles it into an HTML document

## Screenshot

![Screenshot](http://at1as.github.io/github_repo_assets/imdb-scrape.jpg)

## Usage

Download the repository here, set the appropriate permissions and launch IMDB-Scrape via:
```bash
$ git clone https://github.com/at1as/Website-Diff.git
$ cd Website-Diff
$ ./retriever.py
```
All dependencies are listed in retriever.py

## TODO

* Languages, Cast & Genre should be queried as an array, not a string
* Pull up movie results within a modal rather than page redirect
* Small improvements to information retrieval


## Disclaimer

* This product works by scraping the IMDB website. Therefore, problems may arise due to even minor changes to the IDMB website DOM.
* Script is only as good as your movie titles, and IMDB search. If you name files as meticulously as me, they'll almost all be correct (but searches for Fast & Furious, for example, return different results than Fast and Furious)
* IMDB-Scrape was written in (and tested on) Python 2.7
