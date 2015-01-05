# IMDB-Scrape

Gathers information about movies stored in a local directory and compiles it into a searchable HTML document

## Screenshots

#### List of Content
![Screenshot](http://at1as.github.io/github_repo_assets/imdb-scrape.jpg)
#### Movie Details
![Screenshot](http://at1as.github.io/github_repo_assets/imdb-scrape2.jpg)

## Usage

Download the repository here, set the appropriate permissions and launch IMDB-Scrape via:
```bash
$ git clone https://github.com/at1as/Website-Diff.git
$ cd Website-Diff
$ vim conf.json
$ ./retriever.py
```
Set your environment in conf.json:
* max_quantity [Integer] => the maximum number of entries to retrieve from IMDB
* asset_location [String] => the absolute path to the folder containing the files
* exclude_files [Array of Strings] => Exclude these files from retrieval (even if their extensions are included)
* include_extensions [Array of Strings] => files will these extensions (or folders) will be retrieved from IMDB

## Usage Notes
* All dependencies are listed in retriever.py
* Script will only search files in the folder specified by asset_location. Will not search subdirectories
* Movies should, in general, be titled as "Movie Title (YYYY).extension"

## TODO

* Filter: Add options for NOT string
* Viewing: Fix for Chrome not opening Movie Details iframe to the correct height (Google security policy for local files)
* Scraping: If first match is a TV Series, advance to next result

## Disclaimer

* This product works by scraping the IMDB website. Therefore, problems may arise due to even minor changes to the IDMB website DOM.
* Script is only as good as your movie titles, and IMDB search. If you name files meticulously, they'll almost all be correct (but searches for Fast & Furious, for example, return different results than Fast and Furious).
* Only works for movies (documentaries and television entries will be scraped incorrectly)
* IMDB-Scrape was written in (and tested on) Python 2.7
