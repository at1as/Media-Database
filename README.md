# Movie-Database

Gathers information about movies and TV series stored in a local directory and compiles it into static searchable HTML documents.

## Demo

Script output loaded with some randomly chosen sample data is available [here](http://www.jasonwillems.com/sites/mediadatabase/output/). I've tried to include several foreign titles to ensure that they're tagged correctly. Commit used for these reports is now *significantly behind this repo*.

## Screenshots
*As of 20 August 2017*

#### List of Content
<img src="http://at1as.github.io/github_repo_assets/imdb-scrape3.png" width="700px">

#### Movie Details
<img src="http://at1as.github.io/github_repo_assets/imdb-scrape4.png" width="700px">


## Usage

Download the repository here, set the appropriate permissions and launch IMDB-Scrape via:
```bash
$ git clone https://github.com/at1as/IMDB-Scrape.git
$ cd IMDB-Scrape
$ vim conf.json
$ python run.py
```

Titles will be fetched from IMDB the first time the script is run, and then be saved in `_data/movie_data.json`, which the templates are built from. On subsequent runs, only newly added items to the directory will have their data fetched from IMDB.

##### Environment Configuration

Set your environment in `conf.json`:
* *max_quantity* [Integer] => the maximum number of entries to retrieve from IMDB
* *asset_location* [String] => the absolute path to the folder containing the files
* *exclude_files* [Array of Strings] => Exclude these files from retrieval (even if their extensions are included)
* *include_extensions* [Array of Strings] => files will these extensions (or folders) will be retrieved from IMDB. These should all be lower case

##### Removing Entries

For items tagged incorrectly, remove them using the bundled script
```bash
$ python remove_entry.py --movie "<movie_title>" "<YYYY>"
$ python remove_entry.py --series "<series_title>" "<YYYY>"
```
Year is optional. If not provided, first entry with a matching name will removed.

See `$ python remove_entry.py --help` for more details

##### Apache

As the generated output is static content, it can easily be set up for access to generated files across an internal network. Symlink the Apache Documents directory to the root of this repo (IMDB-Scrape), and then access the page at <ip>/IMDB-Scrape/_output/index.html. 


## Usage Notes

##### General Notes

* To view the site in your browser : `$ open _output/index.html`
* All dependencies are listed in retriever.py
* Script will only search files in the folder specified by asset_location. Will not search subdirectories
* Movies should be titled as "Movie Title (YYYY).extension"
* Series should be titled as "Series Title (YYYY).extension"
* Only works for movies, television and documentaries (documentaries will be listed under the movies section)
* Works best in Firefox/Safari. In Chrome, iFrames will be scrollable, rather than resizing to their full height

##### Filters

To use the search filters, items should be comma separated and can be negated with a preceding "!"

For example, in the case of the language input:

* `"English, French, German"` => Returns movies with languages matching English, French, and German
* `"English, !Klingon, Welsh"` => Returns movies with languages matching both English and Welsh, but filters out any with the presence of Klingon
* `"Ger, P"` => Returns movies with languages matching Ger... (i.e., German), P... (i.e., Portuguese, Persian, etc)


## Disclaimer
 
* This product works by scraping the IMDB website. Therefore, problems may arise due to even minor changes to the website layout
* Retrieval is only as good as your movie titles, and IMDB search. Meticulously named files will virtually always be correct, but there may still be some misses
* IMDB-Scrape was written and tested on Python 2.7.10 on OS X (10.11)

### TODO

* FIXME: locally stored glyphicons won't render in Firefox unless they're stored in the same directory
* Generalize Scraper to work with other sites (themoviedb, etc)
* Search by Alternative Title
* Write tests
* Save media info of each series episode
* Add a `--dry-run` flag to skip searching the asset directory and just rebuild site from dumped data
