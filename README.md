# Movie-Database

Gathers information about movies and TV series stored in a local directory and compiles it into static searchable HTML documents.

## Demo

Script output loaded with some randomly chosen sample data is available [here](http://www.jasonwillems.com/sites/mediadatabase/output/). I've tried to include several foreign titles to ensure that they're tagged correctly. Commit used for these reports is now *significantly behind this repo*.

## Screenshots
*As of 20 August 2017*

### List of Content
<img src="http://at1as.github.io/github_repo_assets/imdb-scrape3.png" width="700px">

### Movie Details
<img src="http://at1as.github.io/github_repo_assets/imdb-scrape4.png" width="700px">


## Usage

Download the repository here, set the appropriate permissions and launch Media-Database via:
```bash
$ git clone https://github.com/at1as/Media-Database.git
$ cd Media-Database
$ vim conf.json
$ python run.py
```

Titles will be fetched from IMDB the first time the script is run, and then be saved in `_data/movie_data.json`, which the templates are built from. On subsequent runs, only newly added items to the directory will have their data fetched from IMDB.

#### Dry Run

Run with the `--dry-run` flag to rebuild site from an existing json dump in `_data/movie_data.json`, without adding new entries or needing access to the physical files.
```bash
$ python run --dry-run
```

#### Environment Configuration

Set your environment in `conf.json`:

* *max_quantity* [Integer] => the maximum number of entries to retrieve from IMDB. Play nice; ramp this number up slowly as you build your local database
* *asset_location* [String] => the absolute path to the folder containing the files
* *exclude_files* [Array of Strings] => Exclude these files from retrieval (even if their extensions are included)
* *include_extensions* [Array of Strings] => files will these extensions (or folders) will be retrieved from IMDB. These should all be lower case


#### Removing Entries

For items tagged incorrectly, remove them using the bundled script
```bash
$ python scripts/remove_entry.py --movie "<movie_title>" "<YYYY>"
$ python scripts/remove_entry.py --series "<series_title>" "<YYYY>"
```
Year is optional. If not provided, first entry with a matching name will removed.

See `$ python scripts/remove_entry.py --help` for more details


#### Playback

Some movie listing pages will show an embedded video player. This currently only works in Safari with H264 content which is not a subdirectory


#### Apache

As the generated output is static content, it can easily be set up for access to generated files across an internal network. Symlink the Apache Documents directory to the root of this repo (Media-Database), and then access the page at <ip>/Media-Database/_output/index.html.


## Usage Notes

#### General Notes

* To view the site in your browser : `$ open _output/index.html`
* All dependencies are listed in `setup.py`
* Script will only search files in the folder specified by asset_location. Will not search subdirectories (see below for details)
* Only works for movies, television and documentaries (documentaries will be listed under the movies section, anime will be listed under Series)


#### Movie Asset Locations

Movies should be titled as `Inception (2010).mp4`. If multiple files exist (split movie or separate subtitle files), this format is also acceptable:

```
Inception (2010)/
|── Inception (2010).mp4
└── Inception (2010).srt
```

These pathes are relative to movie location set it `conf.json`


#### Series Asset Locations

* Series should be titled by the name and year, such as `Firefly (2002)` where the year is the start date of the series
* Subtitles should be stored in the same directory as the episodes and should have the exact same title with a different extension
* Episodes may optionally contain titles after the series title and episodes number

```
Firefly (2002)/
└── Firefly Season 1
    └── Firefly S01E01.mp4
    └── Firefly S01E01.srt
    └── Firefly S01E02 The Train Job.mp4
    └── Firefly S01E02 The Train Job.srt
```

These pathes are relative to series location set it `conf.json`


#### Filters

To use the search filters, items should be comma separated and can be negated with a preceding "!"

For example, in the case of the language input:

* `"English, French, German"` => Returns movies with languages matching English, French, and German
* `"English, !Klingon, Welsh"` => Returns movies with languages matching both English and Welsh, but filters out any matches with the presence of Klingon
* `"Ger, P"` => Returns movies with languages matching Ger... (i.e., German), P... (i.e., Portuguese, Persian, etc)


## Disclaimer

* This product works by scraping the IMDB website. Therefore, problems may arise due to even minor changes to the website layout
* Retrieval is only as good as your movie titles, and IMDB search. Meticulously named files will virtually always be correct, but there may still be some misses
* Media-Database was written and tested on Python 2.7.10 on macOS 10.11


### TODO

* FIXME: locally stored glyphicons won't render in Firefox unless they're stored in a child directory
* Add support for other clients (themoviedb, etc)
* Search by Alternative Title
