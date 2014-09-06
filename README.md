# IMDB-Scrape

Gathers information about movies stored in a local directory and compiles it into an HTML document

## Screenshot

![Screenshot](http://at1as.github.io/github_repo_assets/imdb-scrape.jpg)

## Usage

Download the repository here, set the appropriate permissions and launch IMDB-Scrape via:
```bash
$ ./retriever.py
```

## Limitations (and TODO)

* This was thrown together rather quickly, and has some issues. It was tested with 884 files and tagged about 40 of them incorrectly. Improvements will be made.
* Being writing in Python 2.7, Unicode film names are currently posing difficulties. This will be made more robust.
* In some cases, after a failed retrieval, the information from the last movie will be repeated. This will be fixed.

## Disclaimer

This product works by scraping the IMDB website. Therefore, problems may arise due to even minor changes to the IDMB website.

## Dependencies

* Python 2.7
* requests
* lxml.html
* os
* jinja2
