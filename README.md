> ## About this fork
>
> This is a staging fork of [j6k4m8/goosepaper](https://github.com/j6k4m8/goosepaper),
> used to prepare a handful of independent, self-contained changes as separate pull requests.
> Each change lives on its own branch, based directly on `master`, and passes the full test suite
> on its own - none of them depend on this fork being merged as a whole. `mainline` combines all
> of them for local development/testing of a downstream project and is not itself meant to become
> a PR.
>
> | Branch | Adds | Depends on | PR |
> |---|---|---|---|
> | `feature/rss-content-filters` | `content_filters` (CSS-selector/regex cleanup) and `skip_title_patterns` as native, optional fields on the `"rss"` source type - ad/cookie-banner/paywall-stub cleanup and sponsored-post skipping, expressible directly in a goosepaper config. | `master` | [#121](https://github.com/j6k4m8/goosepaper/pull/121) |
> | `feature/puzzle-provider` | A new `"puzzle"` source type: Sudoku, Binoxxo, Futoshiki, Kakuro, and Shikaku, generated and rendered as plain HTML/CSS (no images, no reportlab). Includes a fix for same-type/same-difficulty puzzles (`count > 1`) getting colliding headlines. | `master` | [#123](https://github.com/j6k4m8/goosepaper/pull/123) |
> | `feature/appendix-placement` | A new `PlacementPreference.APPENDIX` value: stories tagged with it render together in their own block at the very end of the document (outside any multi-column container, so page breaks between them are reliable regardless of layout) - the same general pattern already used for `EAR`/`SIDEBAR`/`UTILITY`, just for end-of-document content. | `master` | [#122](https://github.com/j6k4m8/goosepaper/pull/122) |
> | `feature/puzzle-explanations` | Builds on the two branches above: puzzle solutions now render via `PlacementPreference.APPENDIX` instead of an in-place `FULLPAGE` workaround, and a new `explanation` option (`"none"`/`"inline"`/`"footer"`/`"appendix"`) adds an optional short rules blurb per puzzle type, deduplicated across sources via Goosepaper's existing headline-based `deduplicate=True`. | `feature/puzzle-provider`, `feature/appendix-placement` | [#124](https://github.com/j6k4m8/goosepaper/pull/124) |
> | `fix/wikipedia-empty-feed` | `WikipediaCurrentEventsStoryProvider` no longer raises an unhandled `IndexError` when the upstream feed returns zero entries (transient network issues); it now degrades to "no story this run", like an empty RSS feed already does elsewhere. | `master` | [#118](https://github.com/j6k4m8/goosepaper/pull/118) (merged) |
> | `fix/code-block-overflow` | `<pre>`/`<code>` blocks from RSS-sourced articles now wrap (`white-space: pre-wrap` + `overflow-wrap`/`word-break`) instead of silently overflowing into whatever a multi-column layout rendered next to them; `<pre>` also gets a light background/border so it reads as code instead of blending into body text. | `master` | [#120](https://github.com/j6k4m8/goosepaper/pull/120) |
> | `fix/svg-overflow` | Inline `<svg>` icons from RSS-sourced articles no longer render at full column width - `max-width: 100%` constrains ones with an explicit size, and unsized ones (readability strips width/height from every `<svg>` it cleans) get a text-relative `1em x 1em` default instead of filling the container. | `master` | [#119](https://github.com/j6k4m8/goosepaper/pull/119) (merged) |
> | `feature/comic-provider` | A new `"comic"` source type: downloads today's XKCD, Calvin and Hobbes, or Garfield strip and embeds it as an image story. The fetch mechanism (page URL, per-comic headers, `<img>` XPath) is ported from [evidlo/remarkable_news](https://github.com/evidlo/remarkable_news). | `master` | not yet opened |
> | `fix/rss-duplicate-embedded-headline` | `RSSFeedStoryProvider` no longer duplicates the headline when a site's article markup embeds it as a heading inside the same container readability extracts as the article body (Engadget, The Register, MacRumors all confirmed live - see the branch's own commit message for per-site evidence). | `master` | [#134](https://github.com/j6k4m8/goosepaper/pull/134) |
> | `fix/rss-relative-image-urls` | `RSSFeedStoryProvider` now resolves relative `src`/`href` values (`<img>`, `<source>`, `<a>`) in readability-extracted article bodies against the article's own final URL, instead of leaving them relative - goosepaper renders every story from every source as one document with a single `base_url`, so a relative URL from the source page silently fails to load (verified live against current caranddriver.com review pages - see the branch's own commit message). | `master` | [#135](https://github.com/j6k4m8/goosepaper/pull/135) |
>
> Each branch's own commit message has the full rationale and, where relevant, how it was
> verified (test suite + real PDF renders).
>
> **Fork-only fixes - never stage these as a PR branch:** some `mainline` commits exist purely
> to work around one specific misbehaving upstream data source, not a general goosepaper bug -
> opening a PR for them would misrepresent the fix as something every goosepaper user needs.
>
> - `storyprovider/rss.py`'s `html.unescape()` pass on RSS `<title>` (commit `dbd4a08`): The
>   Verge's feed serves titles with entities double-encoded in the raw XML
>   (`AMD&amp;#8217;s ...`) - a bug in their feed generation, not something the RSS 2.0 spec
>   expects consumers to handle, and likely temporary until they fix it on their end. Exotic
>   enough (only reproduced against this one feed so far) that it doesn't belong upstream like
>   the fixes in the table above.

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

RSS sources can filter along two independent axes - what to match (title or fetched article content) and which direction (skip = denylist, accept = allowlist):

|         | Skip (denylist)          | Accept (allowlist)         |
|---------|---------------------------|-------------------------------|
| Title   | `skip_title_patterns`    | `accept_title_patterns`     |
| Content | `skip_content_filters`   | `accept_content_filters`    |

- **`skip_title_patterns` / `accept_title_patterns`** - flat list of regexes, matched case-insensitively against the entry title, before it's even fetched. `skip`: a match drops the entry (e.g. `["^anzeige:", "^sponsored"]` to drop sponsored posts). `accept`: if non-empty, only matches are kept (e.g. `["amazon", "amzn"]` to build a single-company news ticker out of an otherwise general feed).
- **`skip_content_filters`** - list of `{"type": "css", "selector": "..."}` (deletes matching elements, e.g. ad blocks or cookie banners) or `{"type": "regex", "pattern": "...", "flags": "i"}` (strips matching text; `flags` optional, any of `i`/`s`/`m`/`x`) rules. `type` decides which other keys are valid - a `css` entry can't carry `pattern`/`flags`, a `regex` entry can't carry `selector`. Regex rules run first, then CSS rules, regardless of list order.
- **`accept_content_filters`** - list of `{"type": "css", "selector": "..."}` or `{"type": "regex", "pattern": "...", "flags": "i"}` rules, tried/applied independently of each other. `css`: the first selector that matches wins and the article is replaced with just that element's contents - useful when `readability`'s own extraction misses and you know exactly which container holds the real content; no match leaves the article unchanged. `regex`: a whole-story gate rather than a transform - matched against the fetched article's text (not raw markup), so a story is kept only if it matches at least one `regex` filter (e.g. `{"type": "regex", "pattern": "AAPL"}` to keep only articles that actually mention a ticker, the content-level counterpart to `accept_title_patterns`); a `css` filter can't sensibly gate this way, since a miss should leave the article as-is rather than drop it.

RSS sources can also set `min_body_text_length` and/or `max_body_text_length` (both optional, applied after the content filters above) to drop stories whose extracted body's visible text length falls outside that range - `min_body_text_length` catches a failed extraction (a near-empty body), and `max_body_text_length` catches the opposite: an article whose body is implausibly long (e.g. a hardware review with a huge photo gallery/spec dump), which would otherwise balloon a single entry into the bulk of the whole paper.

Any source can also set `"section": "Tech"` to render its stories grouped under that heading, alongside every other source sharing the same section name - useful once a paper mixes several feeds and you want them organized into named groups rather than one flat run of stories. A source with no `"section"` renders ungrouped, same as today.

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
-   [Logic Puzzles](goosepaper/storyprovider/puzzle.py) (this fork's addition - see below)
-   [Daily Comic Strips](goosepaper/storyprovider/comic.py) (this fork's addition - see below)

## puzzle source options

The `"puzzle"` source type (added by this fork) generates one or more logic puzzles - Sudoku,
Binoxxo, Futoshiki, Kakuro, or Shikaku - and renders each as plain HTML/CSS (no images). Every
puzzle's solution is collected separately and placed in the paper's appendix.

```json
{ "type": "puzzle", "puzzle_type": "sudoku", "difficulty": "hard", "count": 2, "explanation": "footer", "name": "Sudoku" }
```

| Option | Required? | Default | What it does |
|---|---|---|---|
| `puzzle_type` | **required** | - | One of `sudoku`, `binoxxo`, `futoshiki`, `kakuro`, `shikaku`. No default on purpose - a config that forgets it fails loudly instead of silently always generating Sudoku. |
| `box_size` | optional | `3` | **Sudoku only**, ignored for every other type. Supported values are `2` (4x4, a quick/easy variant) and `3` (the classic 9x9, 3x3 boxes). Unlike every other type's grid size, this does not vary by `difficulty` - all three difficulties use the same box size. |
| `difficulty` | optional | `"medium"` | One of `easy`, `medium`, `hard`. Controls how many cells/constraints are given, and (for every type but sudoku) the grid size itself - see e.g. `goosepaper/puzzlegen/binoxxo/config.py`'s `DIFFICULTIES` table. Grid size and difficulty aren't independent knobs: Shikaku's "hard" preset, for example, is specifically tuned for a 20x20 grid (a smaller grid can't even fit as many regions as "hard" asks for), so there's no separate `size` option to set independently - it would let a config ask for an untested combination. |
| `count` | optional | `1` | How many puzzle instances of this `puzzle_type`+`difficulty` to generate. |
| `seed` | optional | random | RNG seed, for reproducible generation. |
| `explanation` | optional | `"none"` | `"none"`, `"inline"` (a short rules blurb repeated under every puzzle instance), `"footer"` (a real CSS footnote at the bottom of whichever page it lands on - one footnote per `puzzle_type` in the whole paper, with every instance of that type carrying its own small reference mark pointing at it), or `"appendix"` (one rules blurb per `puzzle_type`, grouped with the solutions at the end of the document). |
| `name` | optional | none | Visible heading for this puzzle instance (and its solution, suffixed " - Lösung"). If omitted, no heading renders for the puzzle itself - only the enclosing section's own title identifies it. Useful when several different puzzle types share one section; redundant (and best left unset) when a section already covers exactly one type+difficulty. |

## comic source options

The `"comic"` source type (added by this fork) downloads today's strip of a daily comic and
embeds it as a single image story. The fetch mechanism (page URL, request headers, and the
`<img>` lookup) for each comic is ported from
[evidlo/remarkable_news](https://github.com/evidlo/remarkable_news), which uses the same
approach to push comics straight to a reMarkable's suspend screen.

```json
{ "type": "comic", "comic_type": "xkcd" }
```

| Option | Required? | Default | What it does |
|---|---|---|---|
| `comic_type` | **required** | - | One of `xkcd`, `cah` (Calvin and Hobbes), `garfield`. No default on purpose - a config that forgets it fails loudly instead of silently always fetching XKCD. |

Every story's headline is a fixed, source-derived name - `"XKCD"`, `"Garfield"`, or
`"Calvin and Hobbes"` - never the strip's own per-day title, and no byline is set. Two comic
sources commonly sit in the same section (e.g. a "Comics" section with both `garfield` and
`cah`); a byline or a per-day dynamic headline would just repeat the same source name the
headline already shows, or produce a needlessly long heading - neither adds anything a reader
can use for a comic, unlike a byline on an RSS article (which distinguishes otherwise-anonymous
entries pulled from different feeds into one section).

Notes per comic:

-   `xkcd`: the strip's real per-day title is still available via the embedded image's `alt`
    attribute, and the mouseover joke text (XKCD's signature `title` attribute) still renders as
    a caption under the image - only the *headline* is fixed to `"XKCD"`.
-   `cah`: gocomics.com requires browser-like request headers, or it blocks the request; those
    are sent automatically. Its page URL is date-scoped (`.../calvinandhobbes/YYYY/MM/DD`), so
    it always resolves to the current day's strip.
-   `garfield`: no title/caption is available on the source page.

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
