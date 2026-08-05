from .config import SourceConfig
from .storyprovider.section import SectionProvider
from .util import (
    clean_text,
    clean_html,
    construct_story_providers_from_source_configs,
    construct_story_providers_from_config_dict,
    htmlize,
)


def test_htmlize():
    assert htmlize(["foo", "bar"]) == "<p>foo</p><p>bar</p>"


def test_clean_html():
    assert clean_html("fooâ€TMbar") == "foo'bar"


def test_clean_text():
    assert clean_text("fooâ€TMbar") == "foo'bar"


def test_construct_story_providers_from_config_dict():
    assert construct_story_providers_from_config_dict({}) == []
    stories = construct_story_providers_from_config_dict(
        {
            "sources": [
                {
                    "type": "text",
                    "headline": "hello",
                    "text": "world",
                }
            ]
        }
    )
    assert len(stories) == 1
    assert stories[0].headline == "hello"

    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "text",
                "headline": "One",
            },
            {
                "type": "text",
                "headline": "Two",
            },
        ]
    )
    assert len(stories) == 2


def test_construct_story_providers_passes_rss_byline_option():
    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "rss",
                "url": "https://example.com/feed.xml",
                "byline": "first",
                "body_source": "summary",
            }
        ]
    )

    assert stories[0].byline_mode == "first"
    assert stories[0].body_source == "summary"


def test_construct_story_providers_passes_rss_content_filter_options():
    """`config.py` only validates that these four fields are well-formed; it's this function's
    own allowed-keys set (see `util.py`) that decides whether a validated field actually reaches
    `RSSFeedStoryProvider` at all. That set is a separate, easy-to-typo copy of the same four
    field names - e.g. a stray plural/singular or skip/accept slip here would pass every
    `test_config.py` check yet silently drop the option in production, since nothing else in the
    test suite drives a config through this exact function. This is the one test that would
    catch that."""
    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "rss",
                "url": "https://example.com/feed.xml",
                "skip_content_filters": [{"type": "css", "selector": "div.ad"}],
                "skip_title_patterns": ["^anzeige:"],
                "accept_content_filters": [{"type": "regex", "pattern": "AAPL"}],
                "accept_title_patterns": ["amazon", "amzn"],
            }
        ]
    )

    assert stories[0].skip_content_filters == [{"type": "css", "selector": "div.ad"}]
    assert stories[0].skip_title_patterns == ["^anzeige:"]
    assert stories[0].accept_content_filters == [{"type": "regex", "pattern": "AAPL"}]
    assert stories[0].accept_title_patterns == ["amazon", "amzn"]


def test_construct_story_providers_passes_rss_body_text_length_options():
    """Same failure mode as test_construct_story_providers_passes_rss_content_filter_options
    above, for min_body_text_length/max_body_text_length specifically: these were added to
    config.py's validation without a matching update to this function's own allowed-keys set,
    so a well-formed config passed every test_config.py check while the values never reached
    RSSFeedStoryProvider at all - silently dropped, filter never actually applied."""
    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "rss",
                "url": "https://example.com/feed.xml",
                "min_body_text_length": 120,
                "max_body_text_length": 4000,
            }
        ]
    )

    assert stories[0].min_body_text_length == 120
    assert stories[0].max_body_text_length == 4000


def test_construct_story_providers_supports_bluesky():
    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "bluesky",
                "username": "jordan.matelsky.com",
                "include_replies": False,
            }
        ]
    )

    assert stories[0].username == "jordan.matelsky.com"
    assert stories[0].include_replies is False
    assert stories[0].feed_filter == "posts_no_replies"


def test_construct_story_providers_supports_readwise(monkeypatch):
    monkeypatch.setenv("GOOSEPAPER_TEST_READWISE_TOKEN", "test-token")

    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "readwise",
                "token_env": "GOOSEPAPER_TEST_READWISE_TOKEN",
                "limit": 3,
                "location": "new",
                "category": "rss",
                "tags": ["daily"],
                "body_source": "text",
            }
        ]
    )

    assert stories[0].token == "test-token"
    assert stories[0].limit == 3
    assert stories[0].location == "new"
    assert stories[0].category == "rss"
    assert stories[0].tags == ["daily"]
    assert stories[0].body_source == "text"


def test_construct_story_providers_passes_weather_breakdown_options():
    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "weather",
                "lat": 36.5,
                "lon": -75.1,
                "mode": "hourly",
                "hours": 12,
                "step_hours": 4,
                "clock_format": "24h",
                "timezone": "America/New_York",
            }
        ]
    )

    assert stories[0].mode == "hourly"
    assert stories[0].hours == 12
    assert stories[0].step_hours == 4
    assert stories[0].clock_format == "24h"
    assert stories[0].timezone == "America/New_York"


def test_construct_story_providers_passes_combined_weather_mode():
    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "weather",
                "lat": 36.5,
                "lon": -75.1,
                "mode": "hourly_daily",
                "hours": 12,
                "step_hours": 4,
                "days": 4,
            }
        ]
    )

    assert stories[0].mode == "hourly_daily"
    assert stories[0].days == 4


def test_construct_story_providers_passes_puzzle_options():
    """Every option construct_story_providers_from_source_configs is supposed to forward to
    PuzzleStoryProvider - including `name`, which is easy to forget here since it's not part of
    the original puzzle_type/box_size/difficulty/count/seed set this provider started with.
    """
    stories = construct_story_providers_from_source_configs(
        [
            {
                "type": "puzzle",
                "puzzle_type": "binoxxo",
                "difficulty": "hard",
                "count": 2,
                "seed": 7,
                "name": "Binoxxo",
            }
        ]
    )

    assert stories[0].puzzle_type == "binoxxo"
    assert stories[0].difficulty == "hard"
    assert stories[0].count == 2
    assert stories[0].seed == 7
    assert stories[0].name == "Binoxxo"


def test_construct_story_providers_passes_comic_type_option():
    stories = construct_story_providers_from_source_configs(
        [{"type": "comic", "comic_type": "garfield"}]
    )

    assert stories[0].comic_type == "garfield"


def test_construct_story_providers_wraps_source_with_section_from_dict():
    providers = construct_story_providers_from_source_configs(
        [
            {"type": "text", "headline": "A", "section": "Tech"},
            {"type": "text", "headline": "B"},
        ]
    )

    assert isinstance(providers[0], SectionProvider)
    assert providers[0].get_stories()[0].section_title == "Tech"

    # No "section" given - stays the bare provider, no group heading assigned.
    assert not isinstance(providers[1], SectionProvider)
    assert providers[1].get_stories()[0].section_title is None


def test_construct_story_providers_wraps_source_with_section_from_source_config():
    """Same as the dict-based test above, but through the SourceConfig objects load_paper_config
    actually produces - the object and dict code paths in _source_config_parts are separate, so
    both need covering."""
    providers = construct_story_providers_from_source_configs(
        [
            SourceConfig(type="text", options={"headline": "A"}, section="Tech"),
            SourceConfig(type="text", options={"headline": "B"}),
        ]
    )

    assert isinstance(providers[0], SectionProvider)
    assert providers[0].get_stories()[0].section_title == "Tech"
    assert not isinstance(providers[1], SectionProvider)
    assert providers[1].get_stories()[0].section_title is None
