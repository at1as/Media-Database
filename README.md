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
$ python retriever.py
```
Set your environment in conf.json:
* *max_quantity* [Integer] => the maximum number of entries to retrieve from IMDB
* *asset_location* [String] => the absolute path to the folder containing the files
* *exclude_files* [Array of Strings] => Exclude these files from retrieval (even if their extensions are included)
* *include_extensions* [Array of Strings] => files will these extensions (or folders) will be retrieved from IMDB

For items tagged incorrectly, remove them using the bundled script
```bash
$ python remove_entry.py "<movie_title>"
```

## Usage Notes

General Notes
* All dependencies are listed in retriever.py
* Script will only search files in the folder specified by asset_location. Will not search subdirectories
* Movies should, in general, be titled as "Movie Title (YYYY).extension"
* Only works for movies (documentaries and television entries will be scraped incorrectly)
* Works best in Firefox/Safari. In Chrome, iFrames will be scrollable, rather than resizing to their full height

Filters
To use the search filters, items should be comma separated and can be negated with a preceding !

For example, in the case of the language input:

* "English, French, German" => Returns movies with languages matching English, French, and German
* "English, !Klingon, Welsh" => Returns movies with languages matching English and Welsh, without the presence of Klingon
* "Ger, P" => Returns movies with languages matching Ger[...] (German), P[...] (Portuguese, Persian, etc)

## Disclaimer
 
* This product works by scraping the IMDB website. Therefore, problems may arise due to even minor changes to the website layout
* Retrieval is only as good as your movie titles, and IMDB search. Meticulously named files will almost all be correct, but there are still likely to be some misses
* IMDB-Scrape was written and tested on Python 2.7.6 on OS X (10.10)
