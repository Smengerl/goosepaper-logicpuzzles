import datetime
import json

import pytest

from . import comic

_XKCD_HTML = b"""
<html><body>
<div id="comic">
<img src="//imgs.xkcd.com/comics/todays_strip.png" title="hover joke text" alt="Todays Strip"/>
</div>
</body></html>
"""


def _gocomics_html(series_name: str = "Calvin and Hobbes") -> bytes:
    ld_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "ComicStory",
            "name": f"{series_name} - January 5, 2026",
            "datePublished": "2026-01-05",
            "isPartOf": {
                "@type": "ComicSeries",
                "name": series_name,
                "url": "https://www.gocomics.com/calvinandhobbes",
            },
        }
    )
    return f"""
    <html><body>
    <script type="application/ld+json">{ld_json}</script>
    <img class="Comic_comic__image__abc123 Comic_comic__abc" src="https://assets.gocomics.com/strip.gif" />
    </body></html>
    """.encode()


def _arcamax_html(series_name: str = "Garfield") -> bytes:
    return f"""
    <html><head>
    <meta property="og:title" content="{series_name}" />
    </head><body>
    <img id="comic-zoom" src="/img/today.jpg" />
    </body></html>
    """.encode()


class _FakeResponse:
    def __init__(self, content: bytes, headers: dict = None, status_code: int = 200):
        self.content = content
        self.headers = headers or {}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise comic.requests.HTTPError(f"{self.status_code} Client Error")
        return None


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Records the pauses the retry logic asks for instead of actually sleeping, and gives
    every test a fresh retry-time budget and request history (both are process-wide state).
    The spacing between requests is switched off here so it doesn't show up in `sleeps`; the
    tests that cover it turn it on explicitly."""
    recorded = []
    monkeypatch.setattr(comic, "_sleep", recorded.append)
    monkeypatch.setattr(comic, "_retry_wait_used_s", 0.0)
    monkeypatch.setattr(comic, "_last_response_at", {})
    monkeypatch.setattr(comic, "_MIN_REQUEST_INTERVAL_S", 0.0)
    return recorded


def test_unknown_comic_type_is_rejected():
    with pytest.raises(ValueError):
        comic.DailyComicStoryProvider(comic_type="dilbert")


def test_gocomics_without_comic_name_is_rejected():
    with pytest.raises(ValueError, match="requires a comic_name"):
        comic.DailyComicStoryProvider(comic_type="gocomics")


def test_arcamax_without_comic_name_is_rejected():
    with pytest.raises(ValueError, match="requires a comic_name"):
        comic.DailyComicStoryProvider(comic_type="arcamax")


def test_xkcd_with_comic_name_is_rejected():
    with pytest.raises(ValueError, match="does not take a comic_name"):
        comic.DailyComicStoryProvider(comic_type="xkcd", comic_name="xkcd")


def test_xkcd_uses_fixed_headline_and_no_byline_but_keeps_hover_text(monkeypatch):
    """XKCD's own per-day title (the <img> alt text, "Todays Strip" in the fixture) is
    deliberately NOT used as the headline - see get_stories()'s docstring on why a fixed,
    source-derived headline (and no byline) is used for every comic instead."""
    calls = []

    def fake_get(url, *, headers, timeout):
        calls.append(url)
        return _FakeResponse(_XKCD_HTML)

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(comic_type="xkcd")
    stories = provider.get_stories()

    assert len(stories) == 1
    story = stories[0]
    assert story.headline == "XKCD"
    # The headline is kept (still names the strip in the table of contents/anchor id) but never
    # rendered above the strip - the strip already shows its own title inside the image.
    assert story.headline_visible is False
    assert story.byline is None
    assert "hover joke text" in story.body_html
    assert 'src="https://imgs.xkcd.com/comics/todays_strip.png"' in story.body_html
    # Only the page is fetched - the strip image is left as a remote link for the render step
    # to fetch/embed later (see get_stories()'s docstring).
    assert calls == ["https://xkcd.com"]


def test_gocomics_uses_date_scoped_url_and_browser_headers_and_derives_label(monkeypatch):
    seen = {"urls": [], "headers": []}

    def fake_get(url, *, headers, timeout):
        seen["urls"].append(url)
        seen["headers"].append(headers)
        return _FakeResponse(_gocomics_html("Calvin and Hobbes"))

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="calvinandhobbes", date=datetime.date(2026, 1, 5)
    )
    stories = provider.get_stories()

    assert seen["urls"] == ["https://www.gocomics.com/calvinandhobbes/2026/01/05"]
    # Only the page fetch needs gocomics.com's browser-like headers - see the "gocomics" entry
    # in _COMIC_SOURCES and get_stories()'s docstring (the strip image itself, on gocomics.com's
    # own CDN, isn't header-gated).
    assert seen["headers"][0]["User-Agent"].startswith("Mozilla/5.0")
    assert seen["headers"][0]["Accept-Language"] == "en"

    story = stories[0]
    # Label is derived from the page's JSON-LD, not hardcoded per comic.
    assert story.headline == "Calvin and Hobbes"
    assert story.headline_visible is False
    assert story.byline is None
    assert story.date == datetime.datetime(2026, 1, 5)
    assert 'src="https://assets.gocomics.com/strip.gif"' in story.body_html


def test_gocomics_derives_label_for_a_different_comic_without_any_code_change(monkeypatch):
    """The whole point of the generic gocomics/arcamax sources: any comic on that site works
    purely by passing a different comic_name, with no new _ComicSource entry or label mapping."""

    def fake_get(url, *, headers, timeout):
        return _FakeResponse(_gocomics_html("Pearls Before Swine"))

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="pearlsbeforeswine", date=datetime.date(2026, 1, 5)
    )
    stories = provider.get_stories()

    assert stories[0].headline == "Pearls Before Swine"


def test_gocomics_missing_label_raises_even_though_image_was_found(monkeypatch):
    """A page with the strip <img> but no (or malformed) JSON-LD indicates the site's template
    changed - fail loudly instead of embedding a comic with no headline."""

    def fake_get(url, *, headers, timeout):
        return _FakeResponse(
            b'<html><body><img class="comic image" src="https://a/strip.gif" /></body></html>'
        )

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="calvinandhobbes", date=datetime.date(2026, 1, 5)
    )
    with pytest.raises(RuntimeError, match="Could not determine the comic's display name"):
        provider.get_stories()


def test_arcamax_derives_label_from_og_title_and_has_no_custom_headers(monkeypatch):
    seen_headers = []

    def fake_get(url, *, headers, timeout):
        seen_headers.append(headers)
        return _FakeResponse(_arcamax_html("Garfield"))

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(comic_type="arcamax", comic_name="garfield")
    stories = provider.get_stories()

    assert seen_headers == [{}]
    assert stories[0].byline is None
    assert stories[0].headline == "Garfield"
    assert 'src="https://www.arcamax.com/img/today.jpg"' in stories[0].body_html


def test_arcamax_derives_label_for_a_different_comic_without_any_code_change(monkeypatch):
    def fake_get(url, *, headers, timeout):
        return _FakeResponse(_arcamax_html("Beetle Bailey"))

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(comic_type="arcamax", comic_name="beetlebailey")
    stories = provider.get_stories()

    assert stories[0].headline == "Beetle Bailey"


def test_missing_strip_image_raises_informative_error(monkeypatch):
    def fake_get(url, *, headers, timeout):
        return _FakeResponse(b"<html><body>no comic here</body></html>")

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(comic_type="xkcd")
    with pytest.raises(RuntimeError, match="Could not find today's strip"):
        provider.get_stories()


def test_gocomics_falls_back_to_previous_day_when_todays_strip_is_missing(monkeypatch, capsys):
    """Regression test: gocomics.com's daily rollover time/timezone isn't documented, so
    generation running earlier in the day than that (unknown) rollover would otherwise fail
    every single time - see comic.py's _MAX_FALLBACK_DAYS docstring. Falling back a day must
    (a) still return the previous day's strip rather than raising, (b) leave no trace of the
    fallback in the Story itself (headline/date/body - the reader shouldn't see a difference),
    and (c) only be surfaced as a log line, per the addon maintainer's explicit call."""
    seen_urls = []

    def fake_get(url, *, headers, timeout):
        seen_urls.append(url)
        if url == "https://www.gocomics.com/calvinandhobbes/2026/01/05":
            return _FakeResponse(b"<html><body>not published yet</body></html>")
        assert url == "https://www.gocomics.com/calvinandhobbes/2026/01/04"
        return _FakeResponse(_gocomics_html("Calvin and Hobbes"))

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="calvinandhobbes", date=datetime.date(2026, 1, 5)
    )
    stories = provider.get_stories()

    assert seen_urls == [
        "https://www.gocomics.com/calvinandhobbes/2026/01/05",
        "https://www.gocomics.com/calvinandhobbes/2026/01/04",
    ]
    story = stories[0]
    # No visible trace of the fallback - same headline/date/body shape as the normal case.
    assert story.headline == "Calvin and Hobbes"
    assert story.date == datetime.datetime(2026, 1, 5)
    assert '<p class="comic-subtitle">' not in story.body_html
    assert 'src="https://assets.gocomics.com/strip.gif"' in story.body_html

    log_output = capsys.readouterr().out
    assert "2026-01-05" in log_output
    assert "2026-01-04" in log_output


def test_gocomics_gives_up_after_max_fallback_days_and_reports_originally_requested_url(
    monkeypatch,
):
    def fake_get(url, *, headers, timeout):
        return _FakeResponse(b"<html><body>never published</body></html>")

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="calvinandhobbes", date=datetime.date(2026, 1, 5)
    )
    with pytest.raises(
        RuntimeError,
        match=r"Could not find today's strip at "
        r"https://www\.gocomics\.com/calvinandhobbes/2026/01/05",
    ):
        provider.get_stories()


def test_xkcd_does_not_retry_across_dates_since_its_url_is_not_date_scoped(monkeypatch):
    """xkcd's page_url has no {date} placeholder, so a miss must raise immediately instead of
    re-fetching the same URL comic._MAX_FALLBACK_DAYS+1 times for no benefit."""
    calls = []

    def fake_get(url, *, headers, timeout):
        calls.append(url)
        return _FakeResponse(b"<html><body>no comic here</body></html>")

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(comic_type="xkcd")
    with pytest.raises(RuntimeError):
        provider.get_stories()

    assert calls == ["https://xkcd.com"]


def test_arcamax_does_not_retry_across_dates_since_its_url_is_not_date_scoped(monkeypatch):
    calls = []

    def fake_get(url, *, headers, timeout):
        calls.append(url)
        return _FakeResponse(b"<html><body>no comic here</body></html>")

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(comic_type="arcamax", comic_name="garfield")
    with pytest.raises(RuntimeError):
        provider.get_stories()

    assert calls == ["https://www.arcamax.com/thefunnies/garfield/"]


# --- retry with backoff on "429 Too Many Requests" -----------------------------------------


def test_429_is_waited_out_and_retried_until_it_succeeds(monkeypatch, sleeps, capsys):
    """gocomics.com blocks a client for a few minutes after a burst of requests. A 429 used to
    drop the comic from the edition; now the same URL is retried after growing pauses."""
    answers = iter(
        [
            _FakeResponse(b"", status_code=429),
            _FakeResponse(b"", status_code=429),
            _FakeResponse(_gocomics_html("Wallace the Brave")),
        ]
    )
    seen_urls = []

    def fake_get(url, *, headers, timeout):
        seen_urls.append(url)
        return next(answers)

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="wallace-the-brave", date=datetime.date(2026, 10, 12)
    )
    stories = provider.get_stories()

    assert stories[0].headline == "Wallace the Brave"
    assert sleeps == [15, 45]
    # The retries hit the very same URL - no date fallback is triggered by a 429.
    assert set(seen_urls) == {"https://www.gocomics.com/wallace-the-brave/2026/10/12"}
    assert len(seen_urls) == 3
    assert "429" in capsys.readouterr().out


def test_persistent_429_raises_after_the_last_retry(monkeypatch, sleeps):
    calls = []

    def fake_get(url, *, headers, timeout):
        calls.append(url)
        return _FakeResponse(b"", status_code=429)

    monkeypatch.setattr(comic.requests, "get", fake_get)

    provider = comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="garfield", date=datetime.date(2026, 10, 12)
    )
    with pytest.raises(comic.requests.HTTPError, match="429"):
        provider.get_stories()

    assert sleeps == [15, 45, 120, 180]
    assert len(calls) == len(comic._RETRY_BACKOFF_S) + 1  # first try + one per pause


def test_total_backoff_covers_the_observed_five_minute_block():
    """Guards the numbers, not the mechanism: the schedule must outlast a ~5 min block."""
    assert sum(comic._RETRY_BACKOFF_S) >= 5 * 60


def test_retry_after_header_lengthens_the_pause_but_is_capped(monkeypatch, sleeps):
    monkeypatch.setattr(comic, "_RETRY_BUDGET_S", 10_000)  # not what this test is about
    answers = iter(
        [
            _FakeResponse(b"", headers={"Retry-After": "100"}, status_code=429),
            _FakeResponse(b"", headers={"Retry-After": "99999"}, status_code=429),
            _FakeResponse(b"", headers={"Retry-After": "soon"}, status_code=429),
            _FakeResponse(_xkcd_ok()),
        ]
    )
    monkeypatch.setattr(comic.requests, "get", lambda url, *, headers, timeout: next(answers))

    comic.DailyComicStoryProvider(comic_type="xkcd").get_stories()

    # 100 > scheduled 15 -> 100; huge value -> capped; unparseable -> scheduled 120.
    assert sleeps == [100, comic._RETRY_AFTER_CAP_S, 120]


def test_503_is_retried_like_429(monkeypatch, sleeps):
    answers = iter([_FakeResponse(b"", status_code=503), _FakeResponse(_xkcd_ok())])
    monkeypatch.setattr(comic.requests, "get", lambda url, *, headers, timeout: next(answers))

    comic.DailyComicStoryProvider(comic_type="xkcd").get_stories()

    assert sleeps == [15]


def test_other_http_errors_are_not_retried(monkeypatch, sleeps):
    calls = []

    def fake_get(url, *, headers, timeout):
        calls.append(url)
        return _FakeResponse(b"", status_code=404)

    monkeypatch.setattr(comic.requests, "get", fake_get)

    with pytest.raises(comic.requests.HTTPError, match="404"):
        comic.DailyComicStoryProvider(comic_type="xkcd").get_stories()

    assert calls == ["https://xkcd.com"]
    assert sleeps == []


def test_retry_time_budget_is_shared_and_stops_further_waiting(monkeypatch, sleeps):
    """One persistent block must not make every comic burn the whole schedule again."""
    monkeypatch.setattr(comic, "_RETRY_BUDGET_S", 70)
    monkeypatch.setattr(
        comic.requests, "get", lambda url, *, headers, timeout: _FakeResponse(b"", status_code=429)
    )

    with pytest.raises(comic.requests.HTTPError):
        comic.DailyComicStoryProvider(comic_type="xkcd").get_stories()
    # 15 + 45 = 60 fits into 70; the next pause (120) would exceed it -> give up.
    assert sleeps == [15, 45]

    sleeps.clear()
    with pytest.raises(comic.requests.HTTPError):
        comic.DailyComicStoryProvider(comic_type="xkcd").get_stories()
    # Only 10 s are left in the budget, so even the first pause (15) no longer fits.
    assert sleeps == []


def _xkcd_ok() -> bytes:
    return _XKCD_HTML


# --- spacing between requests --------------------------------------------------------------


class _FakeClock:
    """A clock that only moves when something sleeps or the test advances it."""

    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture
def clock(monkeypatch):
    fake = _FakeClock()
    monkeypatch.setattr(comic, "_monotonic", fake.monotonic)
    monkeypatch.setattr(comic, "_sleep", fake.sleep)
    monkeypatch.setattr(comic, "_MIN_REQUEST_INTERVAL_S", 1.5)
    return fake


def test_default_request_spacing_is_one_and_a_half_seconds(monkeypatch):
    # The autouse fixture zeroes the constant for the other tests; undo it to see the real one.
    monkeypatch.undo()
    assert comic._MIN_REQUEST_INTERVAL_S == 1.5


def test_requests_to_the_same_host_are_spaced_out(monkeypatch, clock):
    sent_at = []

    def fake_get(url, *, headers, timeout):
        sent_at.append(clock.now)
        clock.now += 0.4  # the request itself takes a moment
        return _FakeResponse(_gocomics_html())

    monkeypatch.setattr(comic.requests, "get", fake_get)

    for slug in ("garfield", "peanuts", "bignate"):
        comic.DailyComicStoryProvider(
            comic_type="gocomics", comic_name=slug, date=datetime.date(2026, 10, 12)
        ).get_stories()

    # The first request goes out at once; every later one waits until 1.5 s after the
    # previous *response* (not request), whichever provider instance sends it.
    assert clock.sleeps == [1.5, 1.5]
    assert sent_at[1] - (sent_at[0] + 0.4) == pytest.approx(1.5)
    assert sent_at[2] - (sent_at[1] + 0.4) == pytest.approx(1.5)


def test_only_the_remaining_time_is_waited_when_something_else_already_took_a_while(
    monkeypatch, clock
):
    def fake_get(url, *, headers, timeout):
        return _FakeResponse(_gocomics_html())

    monkeypatch.setattr(comic.requests, "get", fake_get)
    make = lambda: comic.DailyComicStoryProvider(  # noqa: E731
        comic_type="gocomics", comic_name="garfield", date=datetime.date(2026, 10, 12)
    )

    make().get_stories()
    clock.now += 1.0  # e.g. rendering another section
    make().get_stories()
    clock.now += 5.0  # long enough ago: no wait at all
    make().get_stories()

    assert clock.sleeps == [pytest.approx(0.5)]


def test_different_hosts_do_not_delay_each_other(monkeypatch, clock):
    def fake_get(url, *, headers, timeout):
        return _FakeResponse(_XKCD_HTML if "xkcd" in url else _gocomics_html())

    monkeypatch.setattr(comic.requests, "get", fake_get)

    comic.DailyComicStoryProvider(comic_type="xkcd").get_stories()
    comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="garfield", date=datetime.date(2026, 10, 12)
    ).get_stories()

    assert clock.sleeps == []


def test_date_fallback_requests_are_spaced_too(monkeypatch, clock):
    def fake_get(url, *, headers, timeout):
        if url.endswith("/2026/10/13"):
            return _FakeResponse(b"<html><body>not published yet</body></html>")
        return _FakeResponse(_gocomics_html())

    monkeypatch.setattr(comic.requests, "get", fake_get)

    comic.DailyComicStoryProvider(
        comic_type="gocomics", comic_name="garfield", date=datetime.date(2026, 10, 13)
    ).get_stories()

    assert clock.sleeps == [1.5]


def test_retry_after_a_long_backoff_needs_no_extra_spacing(monkeypatch, clock):
    answers = iter([_FakeResponse(b"", status_code=429), _FakeResponse(_xkcd_ok())])
    monkeypatch.setattr(comic.requests, "get", lambda url, *, headers, timeout: next(answers))

    comic.DailyComicStoryProvider(comic_type="xkcd").get_stories()

    assert clock.sleeps == [15.0]  # only the backoff pause; 15 s already exceeds the spacing
