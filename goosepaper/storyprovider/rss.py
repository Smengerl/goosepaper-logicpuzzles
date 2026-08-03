import datetime
import urllib.parse
from typing import Any, Dict, List, Optional

import feedparser
import requests
from readability import Document

from ..contentfilters import (
    apply_accept_content_filters,
    apply_skip_content_filters,
    should_accept_content,
    should_accept_title,
    should_skip_title,
)
from .storyprovider import StoryProvider
from ..story import Story
from ..version import __version__

RSS_BYLINE_MODES = {"all", "none", "first"}
RSS_BODY_SOURCES = {"auto", "content", "summary", "article"}


class RSSFeedStoryProvider(StoryProvider):
    def __init__(
        self,
        rss_path: str,
        limit: int = 5,
        since_days_ago: int = None,
        byline: str = "all",
        body_source: str = "auto",
        skip_content_filters: Optional[List[Dict[str, Any]]] = None,
        skip_title_patterns: Optional[List[str]] = None,
        accept_content_filters: Optional[List[Dict[str, Any]]] = None,
        accept_title_patterns: Optional[List[str]] = None,
    ) -> None:
        if byline not in RSS_BYLINE_MODES:
            raise ValueError(
                'RSS byline must be one of "all", "none", or "first".'
            )
        if body_source not in RSS_BODY_SOURCES:
            raise ValueError(
                'RSS body_source must be one of "auto", "content", '
                '"summary", or "article".'
            )
        self.limit = limit
        self.feed_url = rss_path
        self.byline_mode = byline
        self.body_source = body_source
        self.skip_content_filters = skip_content_filters or []
        self.skip_title_patterns = skip_title_patterns or []
        self.accept_content_filters = accept_content_filters or []
        self.accept_title_patterns = accept_title_patterns or []
        self._since = (
            datetime.datetime.now() - datetime.timedelta(days=since_days_ago)
            if since_days_ago
            else None
        )

    def get_stories(self) -> List[Story]:
        feed = feedparser.parse(self.feed_url)
        limit = min(self.limit, len(feed.entries))
        if limit == 0:
            print(f"Sad honk :/ No entries found for feed {self.feed_url}...")

        stories = []
        for entry in feed.entries:
            if should_skip_title(entry.get("title", ""), self.skip_title_patterns):
                continue
            if not should_accept_title(entry.get("title", ""), self.accept_title_patterns):
                continue

            date = datetime.datetime(*entry.updated_parsed[:6])
            if self._since is not None and date < self._since:
                continue

            source = _entry_source(entry, self.feed_url)
            story = _story_from_entry(
                entry,
                source,
                date,
                body_source=self.body_source,
            )

            if story is None:
                continue
            if self.accept_content_filters:
                if not should_accept_content(story.body_html, self.accept_content_filters):
                    continue
                story.body_html = apply_accept_content_filters(
                    story.body_html, self.accept_content_filters
                )
            if self.skip_content_filters:
                story.body_html = apply_skip_content_filters(story.body_html, self.skip_content_filters)
            if self.byline_mode == "none":
                story.byline = None
            elif self.byline_mode == "first" and stories:
                story.byline = None

            stories.append(story)
            if len(stories) >= limit:
                break

        return list(filter(None, stories))


def _story_from_entry(
    entry,
    source: str,
    date: datetime.datetime,
    body_source: str = "auto",
) -> Optional[Story]:
    if body_source == "summary":
        return Story(
            entry["title"],
            body_html=_entry_feed_body(entry, preferred="summary"),
            byline=source,
            date=date,
        )

    embedded_content = _entry_embedded_content(entry)
    if embedded_content and body_source != "article":
        return Story(
            entry["title"],
            body_html=embedded_content,
            byline=source,
            date=date,
        )

    link = entry.get("link")
    fallback_body_html = _entry_feed_body(entry, preferred="content")

    if body_source == "content":
        return Story(
            entry["title"],
            body_html=fallback_body_html,
            byline=source,
            date=date,
        )

    if not link:
        return Story(
            entry["title"],
            body_html=fallback_body_html,
            byline=source,
            date=date,
        )

    req = requests.get(
        link,
        headers={"User-Agent": f"goosepaper/{__version__}"},
    )
    if not req.ok:
        return Story(
            entry["title"],
            body_html=fallback_body_html,
            byline=source,
            date=date,
        )

    return _story_from_response(
        entry,
        req,
        source,
        date,
        fallback_body_html=fallback_body_html,
    )


def _story_from_response(
    entry,
    response,
    source: str,
    date: datetime.datetime,
    fallback_body_html: str = "",
) -> Story:
    page_text = response.text
    if not page_text:
        page_text = response.content.decode(
            response.encoding or "utf-8",
            errors="replace",
        )

    try:
        doc = Document(page_text)
        headline = doc.title() or entry["title"]
        body_html = doc.summary() or fallback_body_html
    except Exception:
        headline = entry["title"]
        body_html = fallback_body_html

    return Story(
        headline,
        body_html=body_html,
        byline=source,
        date=date,
    )


def _entry_source(entry, feed_url: str) -> str:
    source_url = entry.get("link") or feed_url
    return urllib.parse.urlparse(source_url).netloc or source_url


def _entry_embedded_content(entry) -> Optional[str]:
    for content_block in entry.get("content", []):
        if not isinstance(content_block, dict):
            continue
        value = content_block.get("value")
        if isinstance(value, str) and value.strip():
            return value
    return None


def _entry_summary(entry) -> str:
    return entry.get("summary") or entry.get("description") or ""


def _entry_feed_body(entry, preferred: str = "content") -> str:
    if preferred == "summary":
        return _entry_summary(entry) or (_entry_embedded_content(entry) or "")
    embedded_content = _entry_embedded_content(entry)
    if embedded_content:
        return embedded_content
    return _entry_summary(entry)
