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

## Limitations (and TODO)

* IMDB-Scrape was written in (and tested on) Python 2.7
* There are still retrieval issues. Was tested with 884 files and misidentified about 40 of them
* In some cases, after a failed retrieval, the information from the last movie will be repeated (might be fixed)
* Doesn't catch error of no results being returned

## Disclaimer

This product works by scraping the IMDB website. Therefore, problems may arise due to even minor changes to the IDMB website DOM.
