Data structure for movies was changed from:

```
    "alternative_title": "xyz"
```

To:

```
    "alternative_title": [
      "xyz"
    ]
```

So that we can hold multiple alternative titles.

Instead of a python backfill script, enter the following into VIM to change the data structure under `_data/movie_data.json` :

```
:%s/\("alternative_title": \)\("\\\)\(.*\)\(\\\""\)/\1\[\3\"\]/g
:%s/"alternative_title": ""/"alternative_title": []/g
```

