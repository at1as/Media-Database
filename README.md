# Media Database

Media Database exists because most streaming interfaces are designed for TVs, not for serious browsing. That pushes them toward large poster grids, shallow filtering, and recommendation-driven discovery. Those products want to keep you inside their algorithm: learn your preferences, surface suggested titles, and decide what you should see next.

This project takes the opposite approach. It is built to be used in a web browser, where dense tables, richer filters, sorting, and text search are far easier to support well. The goal is not algorithmic curation based on personal data. The goal is to give you direct control over your own library so you can refine it across many dimensions and find exactly what you want to watch.

In practice, Media Database indexes locally stored media, enriches it with IMDb metadata, saves that data to local JSON files, and renders a static website for browsing movies, series, and standup.

It is static on purpose. That keeps setup simple, makes the output portable, avoids needing a constantly running local server, and reduces the amount of dependency and runtime management required to use it.

## What It Does

- Scans configured local directories for media files
- Fetches metadata from IMDb using the scraper configured in `conf.json`
- Persists normalized metadata to local JSON repositories in `_data/`
- Builds a static HTML site in `_output/`
- Supports browser-based filtering and sorting across many fields
- Supports movies, series, and standup
- Includes random selection from the current filtered result set
- Lets you customize visible columns in the list view
- Can play media directly in the browser when the file format is supported by the browser

The table view is intentional. This project favors dense, searchable, sortable rows over streaming-style poster browsing.

## Interface

List view is the main working surface: filter aggressively, sort results, and show only the columns you care about.

![List view with dense filtering and configurable columns](docs/images/list-view.png)

Each title also has a detail page for deeper browsing, and compatible files can be played directly in the browser.

![Detail view with title metadata and playback](docs/images/instance-view.png)

## How It Works

1. Configure your media library paths in `conf.json`
2. Run the indexer
3. New titles are looked up on IMDb and stored in local JSON files
4. The site generator renders static pages from those saved JSON files
5. Open the generated site in a browser and use the filters there

Current saved data files:

- `_data/movie_data.json`
- `_data/series_data.json`
- `_data/standup_data.json`

Generated site output:

- `_output/index.html`
- `_output/series.html`
- `_output/standup.html`

## Quick Start

```bash
git clone https://github.com/at1as/Media-Database.git
cd Media-Database
make deps
vim conf.json
make run
```

To rebuild the static site from the existing saved JSON data without scraping new titles:

```bash
make dryrun
```

To open the generated site locally:

```bash
open _output/index.html
```

## Configuration

The project is configured through `conf.json`.

Top-level settings:

- `assets`: per-media-type settings for `movies`, `series`, and `standup`
- `exclude_files`: titles or directories to skip even if they match normal indexing rules
- `include_extensions`: allowed media extensions
- `file_override`: manual IMDb ID overrides for known mismatches
- `pause_time_sec`: delay between remote requests
- `imdb_source`: scraper implementation to use

Each entry in `assets` supports:

- `location`: absolute path to the media directory
- `saved_data`: path to the JSON repository for that media type
- `index_asset`: whether that media type should be scanned
- `max_assets`: cap on how many filesystem entries to inspect
- `max_assets_chunk`: cap on how many new items to process in a single run

## Running and Maintenance

Run the full pipeline:

```bash
make run
```

Run tests:

```bash
make test
```

Remove a bad saved entry so it can be re-scraped:

```bash
python3 scripts/remove_entry.py --movie "<movie_title>" "<YYYY>"
python3 scripts/remove_entry.py --series "<series_title>" "<YYYY>"
```

The year is optional. If omitted, the first matching entry is removed.

## Library Layout

Movies can be single files:

```text
Inception (2010).mp4
```

Or a directory containing the video file and related assets:

```text
Inception (2010)/
|-- Inception (2010).mp4
`-- Inception (2010).srt
```

Series should use a top-level directory named after the show and start year, with episodes inside child directories such as seasons:

```text
Firefly (2002)/
`-- Firefly Season 1
    |-- Firefly S01E01.mp4
    |-- Firefly S01E01.srt
    |-- Firefly S01E02 The Train Job.mp4
    `-- Firefly S01E02 The Train Job.srt
```

## Filtering Model

The generated site is meant to be explored in a browser, not through recommendation feeds. Filtering happens client-side on the rendered data, which makes it easy to combine structured and text-based refinement.

Examples of fields commonly available for filtering or sorting include:

- title
- year
- rating
- genre
- languages
- cast
- director or creator
- running time

The browser UI also supports:

- random selection from the current filtered results
- customizable visible columns in list views
- direct playback on detail pages when the browser supports the media format

Some filters support comma-separated matching and negation with `!`, for example:

- `English, French`
- `English, !Klingon`
- `Ger, Port`

## Notes

- Metadata quality depends on IMDb lookup quality, scraper behavior, and local file naming
- The site is static output, so it can be opened directly from disk, hosted locally, or served on an internal network
- The project currently indexes movies, series, and standup
- Browser filtering is a core product decision, not a secondary feature

## Related Files

- `run.py`: entry point for normal and dry-run execution
- `src/worker.py`: indexing pipeline and JSON persistence
- `src/site_generator.py`: static HTML generation
- `src/scrapers/imdb_suggest.py`: current configured IMDb scraper
- `docs/llm_overview.md`: current architecture and filter behavior overview
