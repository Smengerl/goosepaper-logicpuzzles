> ## About this fork
>
> This is a staging fork of [j6k4m8/goosepaper](https://github.com/j6k4m8/goosepaper),
> used to prepare a handful of independent, self-contained changes as separate pull requests.
> Each change lives on its own branch, based directly on `master`, and passes the full test suite
> on its own - none of them depend on this fork being merged as a whole. `mainline` combines all
> of them for local development/testing of a downstream project and is not itself meant to become
> a PR.
>
> | Branch | Adds | Depends on |
> |---|---|---|
> | `feature/rss-content-filters` | `content_filters` (CSS-selector/regex cleanup) and `skip_title_patterns` as native, optional fields on the `"rss"` source type - ad/cookie-banner/paywall-stub cleanup and sponsored-post skipping, expressible directly in a goosepaper config. | `master` |
> | `feature/puzzle-provider` | A new `"puzzle"` source type: Sudoku, Binoxxo, Futoshiki, Kakuro, and Shikaku, generated and rendered as plain HTML/CSS (no images, no reportlab). Includes a fix for same-type/same-difficulty puzzles (`count > 1`) getting colliding headlines. | `master` |
> | `feature/appendix-placement` | A new `PlacementPreference.APPENDIX` value: stories tagged with it render together in their own block at the very end of the document (outside any multi-column container, so page breaks between them are reliable regardless of layout) - the same general pattern already used for `EAR`/`SIDEBAR`/`UTILITY`, just for end-of-document content. | `master` |
> | `feature/puzzle-explanations` | Builds on the two branches above: puzzle solutions now render via `PlacementPreference.APPENDIX` instead of an in-place `FULLPAGE` workaround, and a new `explanation` option (`"none"`/`"inline"`/`"footer"`/`"appendix"`) adds an optional short rules blurb per puzzle type, deduplicated across sources via Goosepaper's existing headline-based `deduplicate=True`. | `feature/puzzle-provider`, `feature/appendix-placement` |
> | `fix/wikipedia-empty-feed` | `WikipediaCurrentEventsStoryProvider` no longer raises an unhandled `IndexError` when the upstream feed returns zero entries (transient network issues); it now degrades to "no story this run", like an empty RSS feed already does elsewhere. | `master` |
>
> Each branch's own commit message has the full rationale and, where relevant, how it was
> verified (test suite + real PDF renders).

<p align=center><img align=center src='https://raw.githubusercontent.com/j6k4m8/goosepaper/master/docs/goose.svg' width=600 /></p>
<h6 align=center>a daily newsfeed delivered to your remarkable tablet</h6>

<p align=center>
  <a href="https://github.com/j6k4m8/goosepaper/" alt="GitHub repo size"><img src="https://img.shields.io/github/repo-size/j6k4m8/goosepaper?style=for-the-badge" /></a>
  <a href="https://github.com/j6k4m8/goosepaper" alt="GitHub last commit"><img src="https://img.shields.io/github/last-commit/j6k4m8/goosepaper?style=for-the-badge" /></a>
  <a href="https://jordan.matelsky.com" alt="This repo is pretty dope."><img src="https://img.shields.io/badge/pretty%20dope-%F0%9F%91%8C-blue?style=for-the-badge" /></a>
</p>
<p align=center>
  <a href="https://github.com/j6k4m8/goosepaper" alt="This repo is licensed under Apache 2.0"><img src="https://img.shields.io/github/license/j6k4m8/goosepaper?style=for-the-badge" /></a>
  <a href="https://pypi.org/project/goosepaper/"><img alt="PyPI" src="https://img.shields.io/pypi/v/goosepaper?style=for-the-badge"></a>
</p>
<p align=center>
  <a href="https://hub.docker.com/repository/docker/j6k4m8/goosepaper"><img alt="Docker Hub Automated Build" src="https://img.shields.io/badge/DockerHub_image-automated-green?style=for-the-badge"></a>
  <a href="https://github.com/j6k4m8/goosepaper/pkgs/container/goosepaper"><img alt="GitHub Container Registry Automated build" src="https://img.shields.io/badge/GHCR.io_image-automated-green?style=for-the-badge"></a>
 </p>
 <p align=center>
  <a href="https://github.com/j6k4m8/goosepaper/actions?query=workflow%3A%22Python+Tests%22"><img alt="GitHub Workflow Status (with branch)" src="https://img.shields.io/github/actions/workflow/status/j6k4m8/goosepaper/python-package.yml?branch=master&style=for-the-badge"></a>
  <a href="https://codecov.io/gh/j6k4m8/goosepaper"><img alt="Codecov" src="https://img.shields.io/codecov/c/github/j6k4m8/goosepaper?logo=codecov&style=for-the-badge"></a>
</p>

## what's up

goosepaper is a utility that delivers a daily newspaper to your remarkable tablet. that's cute!

you can include RSS feeds, Mastodon feeds, news articles, wikipedia articles-of-the-day, weather, and more. I read it when I wake up so that I can feel anxious without having to get my phone.

## public instance

https://goosepaper.jordan.matelsky.com/

## get started with docker

By far the easiest way to get started with Goosepaper is to use Docker.

### step 0: write your config file

Write a paper config file to tell Goosepaper what news you want to read. An example is provided in `example-config.json`.

### step 1: generate your paper

From the directory that has the config file in it, run the following:

```shell
docker run -it --rm -v $(pwd):/goosepaper/mount j6k4m8/goosepaper goosepaper -c mount/example-config.json -o mount/Goosepaper.pdf
```

(where `example-config.json` is the name of the config file to use).

### step 2: you are done!

If you want to both generate the PDF and deliver it to your reMarkable tablet, pass `--deliver`. You must additionally mount your `~/.rmapi` file:

```shell
docker run -it --rm \
    -v $(pwd):/goosepaper/mount \
    -v $HOME/.rmapi:/root/.rmapi \
    j6k4m8/goosepaper \
    goosepaper -c mount/example-config.json -o mount/Goosepaper.pdf --deliver
```

Otherwise, you can now email this PDF to your tablet, perhaps using [ReMailable](https://github.com/j6k4m8/remailable).

## get started without docker: installation

### dependencies:

this tool uses `weasyprint` to generate PDFs. After installing the system prerequisites below, sync the project environment with `uv sync`.

more details [here](https://weasyprint.readthedocs.io/en/latest/install.html).

Goosepaper now targets Python 3.12+.

#### mac:

```shell
brew install cairo pango gdk-pixbuf libffi
```

#### ubuntu-flavored:

```shell
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

#### windows:

[Follow these instructions carefully](https://weasyprint.readthedocs.io/en/latest/install.html#windows).

## and then:

From inside the goosepaper repo,

```shell
uv sync
```

Then run Goosepaper through uv:

```shell
uv run goosepaper --config myconfig.json --output mypaper.pdf
```

## get started

You can customize your goosepaper by editing a paper config file. If you do not pass `--config`, Goosepaper looks for `./goosepaper.json`.

```shell
uv run goosepaper --config myconfig.json --output mypaper.pdf
```

If you don't pass an output flag, one will be generated based upon the time of generation.

The paper config uses a strict v2 schema with one file per paper. A minimal example looks like this:

```json
{
  "version": 2,
  "paper": {
    "style": "FifthAvenue",
    "font_size": 14,
    "table_of_contents": true,
    "layout": "auto",
    "page_profile": "remarkable2"
  },
  "sources": [
    {
      "type": "rss",
      "url": "https://feeds.npr.org/1001/rss.xml",
      "limit": 5,
      "byline": "first",
      "body_source": "auto"
    },
    { "type": "reddit", "subreddit": "news" }
  ],
  "delivery": {
    "folder": "Morning Brief"
  }
}
```

`style` selects a visual theme. `layout` controls the overall column density: with `"auto"`, Goosepaper defaults to a single reading column on narrow device profiles like `remarkable1`, `remarkable2`, and `paper_pro_move`, and to denser multi-column pages on larger profiles like `paper_pro`, `letter`, and `a4`. If you want to force it, set `"layout": "1col"`, `"2col"`, or `"3col"`. If you want a linked contents block near the top of the issue, set `"table_of_contents": true` in the `paper` object. If you want to override the body typeface without taking over the whole design, set `"body_font": "Literata"`. If you want to target a specific device or paper shape, set `"page_profile"` to one of `remarkable1`, `remarkable2`, `paper_pro`, `paper_pro_move`, `letter`, or `a4`. (`"rm1"` also works as a short alias.) RSS sources can also set `"byline": "all"`, `"none"`, or `"first"`, plus `"body_source": "auto" | "content" | "summary" | "article"`. Bluesky sources can set `"include_replies": true | false`. Weather sources can set `"mode": "summary" | "hourly" | "daily" | "hourly_daily"` plus `hours`, `step_hours`, `days`, and `clock_format` for richer forecasts.

Delivery still happens only when you pass `--deliver`. If you want user-level delivery defaults, create `~/.config/goosepaper/config.json`:

```json
{
    "version": 2,
    "delivery_defaults": {
        "folder": "News",
        "replace_mode": "nocase",
        "cleanup": true
    }
}
```

CLI flags override the config for a single run:

```shell
uv run goosepaper --deliver --folder Inbox --replace-mode exact
```

An example config file is included here: [example-config.json](example-config.json).

---

Check out [this example PDF](https://github.com/j6k4m8/goosepaper/blob/master/docs/Example-Nov-1-2020.pdf), generated on Nov 1 2020.

## existing story providers ([want to write your own?](https://github.com/j6k4m8/goosepaper/blob/master/CONTRIBUTING.md))

-   [Wikipedia Top News / Current Events](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/wikipedia.py)
-   [Mastodon Toots](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/mastodon.py)
-   [Bluesky Posts](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/bluesky.py)
-   [Readwise Reader Documents](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/readwise.py)
-   [Weather](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/weather.py). These stories appear in the "ear" of the front page, just like a regular ol' newspaper
-   [RSS Feeds](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/rss.py)
-   [Reddit Subreddits](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/reddit.py)

# More Questions, Infrequently Asked

### yes but pardon me — i haven't a remarkable tablet

Do you have another kind of tablet? You may generate a print-ready PDF which you can use on another kind of robot as well! Just remove the last line of `main.py`.

### very nice! may i have it in comic sans?

yes! you may do anything that you find to be fun and welcoming :)

If you want a real override, set `paper.body_font` in your paper config and let the rest of the layout and typography engine keep doing its job.

### do all dogs' names start with the letter "B"?

I do not think so, but it is a good question!

### may i use this to browse twitter?

~~yes you may! you can add a list of usernames to the feed generator and it will make a print-ready version of twitter. this is helpful for when you are on twitter on your laptop but wish you had Other Twitter as well, in print form.~~

no! twitter has changed and now no one can play nicely with them. sorry! it is sad!

# You May Also Like...

-   [remailable](https://github.com/j6k4m8/remailable): Email PDF documents to your reMarkable tablet
-   [remarkapy](https://github.com/j6k4m8/remarkapy): My Python client for the reMarkable cloud API, which powers the upload functionality of Goosepaper
