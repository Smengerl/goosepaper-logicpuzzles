from __future__ import annotations

import importlib.resources as resources
from dataclasses import dataclass


@dataclass(frozen=True)
class PageProfile:
    name: str
    size: str
    margin_top: str
    margin_right: str
    margin_bottom: str
    margin_left: str
    max_auto_columns: int


_PAGE_PROFILES = {
    "rm1": PageProfile(
        name="rm1",
        size="6.18in 8.24in",
        margin_top="0.34in",
        margin_right="0.24in",
        margin_bottom="0.26in",
        margin_left="0.24in",
        max_auto_columns=2,
    ),
    "remarkable1": PageProfile(
        name="remarkable1",
        size="6.18in 8.24in",
        margin_top="0.34in",
        margin_right="0.24in",
        margin_bottom="0.26in",
        margin_left="0.24in",
        max_auto_columns=2,
    ),
    "remarkable2": PageProfile(
        name="remarkable2",
        size="6.18in 8.24in",
        margin_top="0.34in",
        margin_right="0.24in",
        margin_bottom="0.26in",
        margin_left="0.24in",
        max_auto_columns=2,
    ),
    "paper_pro": PageProfile(
        name="paper_pro",
        size="7.08in 9.44in",
        margin_top="0.36in",
        margin_right="0.26in",
        margin_bottom="0.28in",
        margin_left="0.26in",
        max_auto_columns=2,
    ),
    "paper_pro_move": PageProfile(
        name="paper_pro_move",
        size="3.58in 6.36in",
        margin_top="0.22in",
        margin_right="0.16in",
        margin_bottom="0.20in",
        margin_left="0.16in",
        max_auto_columns=1,
    ),
    "letter": PageProfile(
        name="letter",
        size="8.5in 11in",
        margin_top="0.52in",
        margin_right="0.34in",
        margin_bottom="0.38in",
        margin_left="0.34in",
        max_auto_columns=2,
    ),
    "a4": PageProfile(
        name="a4",
        size="210mm 297mm",
        margin_top="13mm",
        margin_right="9mm",
        margin_bottom="10mm",
        margin_left="9mm",
        max_auto_columns=2,
    ),
}


PAGE_PROFILE_CHOICES = tuple(_PAGE_PROFILES)

_THEME_FONTS = {
    "Academy": {
        "body": 'Georgia, "Times New Roman", serif',
        "display": '"Times New Roman", Georgia, serif',
        "sans": '"Times New Roman", Georgia, serif',
    },
    "Autumn": {
        "body": 'Georgia, "Times New Roman", serif',
        "display": '"Playfair Display", Georgia, serif',
        "sans": '"Oswald", "Helvetica Neue", sans-serif',
    },
    "FifthAvenue": {
        "body": '"Open Sans", "Helvetica Neue", sans-serif',
        "display": '"Source Serif Pro", Georgia, serif',
        "sans": '"Open Sans", "Helvetica Neue", sans-serif',
    },
    "GrayMaiden": {
        "body": '"Source Serif 4", Georgia, serif',
        "display": '"Newsreader", Georgia, serif',
        "sans": '"Libre Franklin", "Helvetica Neue", sans-serif',
    },
}

_THEME_AUTO_COLUMNS = {
    "Academy": 1,
    "FifthAvenue": 2,
    "Autumn": 2,
    "GrayMaiden": 2,
}


def read_stylesheets(path) -> list[str]:
    if path.is_file():
        return path.read_text().strip("\n").split("\n")
    return []


def read_css(path):
    return path.read_text()


class Style:
    def __init__(self, style: str = ""):
        self.style_name = style or "FifthAvenue"
        if not self.read_style(self.style_name):
            if style:
                print(f"Oops! {style} style not found or broken. Use default style.")
            self.style_name = "FifthAvenue"
            self.read_style(self.style_name)

    def get_stylesheets(self) -> list[str]:
        return list(getattr(self, "_stylesheets", []))

    def get_page_profile(self, page_profile: str = "remarkable2") -> PageProfile:
        profile_name = page_profile or "remarkable2"
        if profile_name not in _PAGE_PROFILES:
            print(
                f"Oops! {profile_name} page profile not found or broken. Use default page profile."
            )
            profile_name = "remarkable2"
        return _PAGE_PROFILES[profile_name]

    def get_css(
        self,
        font_size: int = 14,
        body_font: str | None = None,
        layout: str = "auto",
        page_profile: str = "remarkable2",
    ) -> str:
        profile = self.get_page_profile(page_profile)
        effective_columns = self.resolve_column_count(layout, page_profile)
        css_parts = [
            _base_print_css(profile, font_size, effective_columns),
            getattr(self, "_css", ""),
        ]
        if body_font:
            css_parts.append(_body_font_override_css(body_font))
        return "\n".join(css_parts)

    def get_epub_css(self, font_size: int = 14, body_font: str | None = None) -> str:
        theme_fonts = _THEME_FONTS.get(self.style_name, _THEME_FONTS["FifthAvenue"])
        body_stack = _font_stack(body_font, theme_fonts["body"])
        return f"""
        body {{
            font-family: {body_stack};
            font-size: {float(font_size):.2f}pt;
            line-height: 1.42;
        }}

        .story-headline,
        h1, h2, h3 {{
            font-family: {theme_fonts["display"]};
        }}

        .byline {{
            font-family: {theme_fonts["sans"]};
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        """

    def read_style(self, style: str) -> bool:
        for root in _style_roots():
            css, stylesheets = _read_style_from_root(root, style)
            if css is not None:
                self._stylesheets = stylesheets
                self._css = css
                return True
        return False

    def resolve_column_count(
        self, layout: str = "auto", page_profile: str = "remarkable2"
    ) -> int:
        profile = self.get_page_profile(page_profile)
        if layout == "auto":
            default_columns = _THEME_AUTO_COLUMNS.get(self.style_name, 2)
            return max(1, min(default_columns, profile.max_auto_columns))
        return {"1col": 1, "2col": 2, "3col": 3}.get(layout, profile.max_auto_columns)


def _style_roots():
    yield resources.files("goosepaper").joinpath("assets", "styles")


def _read_style_from_root(root, style):
    path = root.joinpath(style)
    if path.is_dir():
        css_file = next(
            (entry for entry in path.iterdir() if entry.name.endswith(".css")),
            None,
        )
        if css_file is None:
            return None, []
        return read_css(css_file), read_stylesheets(path.joinpath("stylesheets.txt"))

    css_path = root.joinpath(f"{style}.css")
    if css_path.is_file():
        return read_css(css_path), []

    return None, []


def _parse_length_inches(value: str) -> float:
    """Parses a PageProfile length ("6.18in", "9mm") into inches - the only two units any bundled
    page_profile currently uses (see `_PAGE_PROFILES` above). The canonical copy: goosepaper.py
    has its own use for the same parsing (deriving an embedded-image pixel cap from page
    geometry) and imports this one rather than keeping a second copy - PageProfile itself lives
    here, so this is that copy's natural home. Assuming one specific unit here would silently
    break every profile written in another - an inch-only version of this shipped briefly in
    `_comic_image_max_height_in()` below and would have raised on `page_profile: "a4"` (mm-based)
    the first time anyone used it, never actually released."""
    value = value.strip()
    if value.endswith("mm"):
        return float(value[:-2]) / 25.4
    if value.endswith("in"):
        return float(value[:-2])
    raise ValueError(f"Unsupported page_profile length unit: {value!r}")


# `article.story-short > .story-headline`'s own font-size/line-height/margin-bottom (see the CSS
# block below) - named here, and referenced from both that block and
# _comic_image_max_height_in(), specifically so the two can never silently drift apart the way
# two independently hand-copied sets of the same three numbers eventually would.
_STORY_SHORT_HEADLINE_FONT_SIZE_EM = 1.16
_STORY_SHORT_HEADLINE_LINE_HEIGHT = 1.12
_STORY_SHORT_HEADLINE_MARGIN_BOTTOM_REM = 0.28


def _comic_image_max_height_in(profile: PageProfile, font_size: int) -> float:
    """How tall a comic image is allowed to get before WeasyPrint's page-break-inside "avoid" on
    its article (see storyprovider/comic.py's short_form comment) stops being reliable - derived
    from the page profile actually in use and the configured font size, not a flat guess. A strip
    scaled to exactly this height is guaranteed to leave room for its own headline above it on a
    fresh page, on any page profile: profiles vary a lot in absolute size (e.g. "paper_pro" at
    9.44in tall vs. "paper_pro_move" at 6.36in), but the headline's own height barely does (it
    tracks font_size, not page size) - so a single hardcoded height, and *especially* a single
    hardcoded fraction of page height (which was tried first, and calibrated against only one
    profile by accident), both drift wrong on every other profile.

    Reserves 2 lines' worth of the headline's own font-size/line-height - covers a comic label
    long enough to wrap at a narrow page width (e.g. "Wallace The Brave") without needing to
    special-case it - plus that headline's own margin-bottom, plus a small fixed buffer for
    rounding/border effects that isn't worth computing exactly. font_size arrives in points
    (goosepaper's own unit for it throughout - see `body { font-size: ...pt }` below) and is
    converted to inches (1in = 72pt) to match _parse_length_inches, rather than the other way
    around, so this stays consistent with how the rest of the codebase already parses
    PageProfile lengths (see this function's own docstring).
    """
    content_height_in = (
        _parse_length_inches(profile.size.split()[1])
        - _parse_length_inches(profile.margin_top)
        - _parse_length_inches(profile.margin_bottom)
    )
    headline_pt = font_size * _STORY_SHORT_HEADLINE_FONT_SIZE_EM
    two_lines_pt = 2 * headline_pt * _STORY_SHORT_HEADLINE_LINE_HEIGHT
    margin_bottom_pt = font_size * _STORY_SHORT_HEADLINE_MARGIN_BOTTOM_REM
    reserved_in = (two_lines_pt + margin_bottom_pt) / 72 + 0.06  # + small fixed buffer
    return content_height_in - reserved_in


def _base_print_css(
    profile: PageProfile, font_size: int, effective_columns: int
) -> str:
    toc_columns = 1 if effective_columns == 1 else 2
    comic_image_max_height_in = _comic_image_max_height_in(profile, font_size)
    return f"""
    @page {{
        size: {profile.size};
        margin-top: {profile.margin_top};
        margin-right: {profile.margin_right};
        margin-bottom: {profile.margin_bottom};
        margin-left: {profile.margin_left};
    }}

    * {{
        box-sizing: border-box;
    }}

    html {{
        color: #111;
    }}

    body {{
        margin: 0;
        color: #111;
        font-size: {int(font_size)}pt;
        line-height: 1.45;
    }}

    a {{
        color: inherit;
    }}

    p,
    ul,
    ol,
    blockquote,
    figure {{
        margin-top: 0.45rem;
        margin-bottom: 0.75rem;
    }}

    ul,
    ol {{
        padding-left: 1.2rem;
    }}

    li {{
        margin-bottom: 0.18rem;
    }}

    img {{
        max-width: 100%;
        height: auto;
    }}

    /* Article HTML pulled in via RSS/readability sometimes keeps interactive UI controls from
    the source page - most commonly an image "click to zoom" lightbox trigger button (a common
    WordPress/Gutenberg pattern), typically an icon-only <button> whose real position/visibility
    is set by JavaScript that never runs here. Unpositioned, it falls into normal document flow
    as an empty-looking box using the browser/WeasyPrint UA stylesheet's default <button>
    styling (grey background, border, rounded corners) - it reads as a flat grey block with
    nothing legible inside, since it typically contains only an icon (often a light-on-dark SVG
    that's invisible against that same default grey). No <button> in extracted article prose is
    ever meaningfully interactive in a static, print/PDF context, so hide every one uniformly
    rather than chase each source site's specific button/icon markup one at a time. */
    button {{
        display: none;
    }}

    /* `<pre>`'s default `white-space: pre` never wraps long lines - fine in a browser (you get a
    scrollbar), but there's no scrolling on a printed/PDF page, so a code block wider than its
    column just overflowed into whatever rendered next to it (visually overlapping the next
    column's text in a multi-column layout). pre-wrap keeps line breaks/indentation but allows
    wrapping; break-word/break-all as a second line of defense for a single unbroken token (a long
    URL, hash, or identifier) that's still wider than the column on its own. */
    pre, code {{
        white-space: pre-wrap;
        overflow-wrap: break-word;
        word-break: break-word;
    }}

    pre {{
        max-width: 100%;
        overflow: hidden;
        margin: 0.5rem 0;
        padding: 0.5rem 0.65rem;
        background: #f4f4f4;
        border: 0.75pt solid #ddd;
        border-radius: 3px;
        font-size: 0.85em;
        line-height: 1.35;
    }}

    :not(pre) > code {{
        background: #f4f4f4;
        padding: 0.05em 0.3em;
        border-radius: 2px;
    }}

    /* Article HTML pulled in via RSS/readability sometimes keeps interactive UI controls from
    the source page - most commonly an image "click to zoom" lightbox trigger button (a common
    WordPress/Gutenberg pattern), typically an icon-only <button> whose real position/visibility
    is set by JavaScript that never runs here. Unpositioned, it falls into normal document flow
    as an empty-looking box using the browser/WeasyPrint UA stylesheet's default <button>
    styling (grey background, border, rounded corners) - it reads as a flat grey block with
    nothing legible inside, since it typically contains only an icon (often a light-on-dark SVG
    that's invisible against that same default grey). No <button> in extracted article prose is
    ever meaningfully interactive in a static, print/PDF context, so hide every one uniformly
    rather than chase each source site's specific button/icon markup one at a time. */
    button {{
        display: none;
    }}

    /* Inline <svg> (decorative icons/illustrations some source sites embed directly in article
    HTML) has no such constraint by default - unlike <img>, which browsers/WeasyPrint shrink to
    fit an ancestor's width automatically in most contexts, an <svg> renders at its own
    width/height (or viewBox-implied size) regardless of the column it landed in. Observed: a
    corner-bracket icon rendering the better part of a page tall/wide in a narrow newspaper
    column. Same fix as <img>: cap it to the column and let it scale down proportionally. */
    svg {{
        max-width: 100%;
        height: auto;
    }}

    /* max-width caps an SVG that's too big, but doesn't help one with no size at all: readability
    (goosepaper's HTML extractor) strips width/height attributes from every <svg> during cleaning,
    even ones the source page did give an explicit size (verified: readability.Document(html) with
    an svg width="20px" height="20px" comes back with neither). A replaced element with only a
    viewBox and no intrinsic width/height defaults to filling its container's available width -
    turning a small UI icon (a code block's "copy"/"fullscreen" button, meant to render around
    text-height) into a shape as wide as the column. Give it a small, text-relative default size
    instead - covers every <svg> goosepaper ever sees, since none of them keep their width
    attribute this far into the pipeline regardless of what the source page originally had. */
    svg:not([width]) {{
        width: 1em;
        height: 1em;
    }}

    .header {{
        position: relative;
        margin: 0 0 0.65rem;
        padding: 0 0 0.55rem;
        border-bottom: 1.5pt solid #111;
    }}

    body.has-toc .header {{
        margin-bottom: 0.35rem;
    }}

    .header::after,
    .stories::after {{
        content: "";
        display: block;
        clear: both;
    }}

    .header .ear {{
        width: 24%;
        font-size: 0.76em;
    }}

    .header .left-ear {{
        float: left;
        margin: 0.25rem 1rem 0 0;
    }}

    .header .right-ear {{
        float: right;
        margin: 0.25rem 0 0 1rem;
    }}

    .header .ear:empty,
    .sidebar:empty {{
        display: none;
    }}

    .header.has-left-ear .masthead {{
        margin-left: 26%;
    }}

    .header.has-right-ear .masthead {{
        margin-right: 26%;
    }}

    .header.has-left-ear.has-right-ear .masthead {{
        margin-left: 20%;
        margin-right: 20%;
    }}

    .masthead {{
        min-height: 3.5rem;
    }}

    .masthead h1 {{
        margin: 0;
        line-height: 0.95;
    }}

    .edition-line {{
        margin: 0.3rem 0 0;
        font-size: 0.86em;
        line-height: 1.25;
    }}

    .table-of-contents {{
        margin: 0 0 0.85rem;
        padding: 0.15rem 0 0.45rem;
        border-bottom: 0.9pt solid #d2d2d2;
    }}

    .table-of-contents__label {{
        margin: 0 0 0.35rem;
        font-size: 0.7em;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }}

    .table-of-contents__entries {{
        margin: 0;
        column-count: {toc_columns};
        column-gap: 1.4rem;
    }}

    .table-of-contents__entry {{
        break-inside: avoid;
        margin-bottom: 0.3rem;
    }}

    .table-of-contents__link {{
        display: block;
        text-decoration: none;
    }}

    .table-of-contents__link::after {{
        content: leader(dotted) target-counter(attr(href), page);
    }}

    .utility-strip {{
        margin: 0 0 0.85rem;
        padding: 0.15rem 0 0.5rem;
        border-bottom: 0.9pt solid #d2d2d2;
    }}

    .utility-strip > article {{
        margin: 0;
        padding: 0.15rem 0 0.25rem;
        border-bottom: 0;
    }}

    .utility-strip > article + article {{
        margin-top: 0.65rem;
        padding-top: 0.55rem;
        border-top: 0.9pt solid #d9d9d9;
    }}

    .utility-strip article > h1 {{
        margin-bottom: 0.3rem;
        font-size: 1.02em;
        line-height: 1.1;
    }}

    .weather-kicker {{
        margin: 0 0 0.35rem;
        font-size: 0.72em;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }}

    .weather-module__section + .weather-module__section {{
        margin-top: 0.55rem;
        padding-top: 0.5rem;
        border-top: 0.9pt solid #d9d9d9;
    }}

    .weather-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }}

    .weather-table__cell {{
        padding: 0 0.28rem;
        border-left: 0.9pt solid #d9d9d9;
        vertical-align: top;
        text-align: center;
    }}

    .weather-table__cell:first-child {{
        padding-left: 0;
        border-left: 0;
    }}

    .weather-table__cell:last-child {{
        padding-right: 0;
    }}

    .weather-cell__label,
    .weather-cell__temp,
    .weather-cell__condition {{
        display: block;
    }}

    .weather-cell__label {{
        font-size: 0.68em;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    .weather-cell__temp {{
        margin-top: 0.08rem;
        font-size: 1.12em;
        font-weight: 700;
        line-height: 1.05;
    }}

    .weather-cell__condition {{
        margin-top: 0.12rem;
        font-size: 0.72em;
        line-height: 1.2;
    }}

    .weather-empty {{
        margin: 0;
        font-size: 0.8em;
    }}

    .stories {{
        width: 100%;
    }}

    .main-stories,
    .sidebar {{
        width: 100%;
    }}

    .main-stories {{
        column-gap: 1.35rem;
        column-fill: balance;
    }}

    .stories--1col .main-stories {{
        column-count: 1;
    }}

    .stories--2col:not(.has-sidebar) .main-stories {{
        column-count: 2;
    }}

    .stories--3col:not(.has-sidebar) .main-stories {{
        column-count: 3;
        column-gap: 1rem;
    }}

    .stories--2col.has-sidebar .main-stories {{
        width: 100%;
        column-count: 2;
    }}

    .stories--2col.has-sidebar .sidebar {{
        display: block;
        width: 100%;
        margin-top: 0.85rem;
        padding-top: 0.7rem;
        border-top: 0.9pt solid #d2d2d2;
        column-count: 2;
        column-gap: 1.2rem;
    }}

    .stories--3col.has-sidebar .main-stories {{
        width: 100%;
        column-count: 3;
    }}

    .stories--3col.has-sidebar .sidebar {{
        display: block;
        width: 100%;
        margin-top: 0.85rem;
        padding-top: 0.7rem;
        border-top: 0.9pt solid #d2d2d2;
        column-count: 2;
        column-gap: 1.2rem;
    }}

    .stories--1col.has-sidebar .sidebar {{
        display: block;
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 0.9pt solid #d2d2d2;
    }}

    .sidebar-title {{
        margin: 0 0 0.6rem;
        font-size: 0.72em;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }}

    .story-section-heading {{
        break-after: avoid;
        margin: 0 0 0.55rem;
        padding-top: 0.08rem;
    }}

    .story-section-title {{
        margin: 0;
        font-size: 0.72em;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }}

    article {{
        margin: 0;
        text-align: left;
    }}

    /* One guaranteed break before the appendix block as a whole starts - so it never begins
    mid-page, tacked onto whatever the last regular/sidebar content happened to leave room for.
    This is on .appendix itself, not .appendix > article, precisely so it fires exactly once:
    a rule on every article would repeat the break-per-story behavior this same file already
    removed on purpose (see the comment below) for wasting a page per entry. */
    .appendix {{
        break-before: page;
    }}

    /* Appendix stories (PlacementPreference.APPENDIX) render in their own block after
    everything else - just placed at the end, one after another in the normal flow, same as
    .main-stories/.sidebar articles. No per-story page break: that would waste a page per story
    for something like a puzzle's solution, where a plain divider is enough. */
    .main-stories > article,
    .sidebar > article,
    .appendix > article {{
        margin-bottom: 1rem;
        padding-bottom: 0.9rem;
        border-bottom: 0.9pt solid #d9d9d9;
    }}

    .main-stories > article:last-child,
    .sidebar > article:last-child,
    .appendix > article:last-child {{
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: 0;
    }}

    article > h1,
    article > h2,
    article > h3 {{
        margin-top: 0;
        break-after: avoid;
    }}

    article > .byline {{
        margin: 0 0 0.55rem;
        font-size: 0.75em;
    }}

    /* short_form stories (puzzles, weather, reddit/bluesky posts, comics) are compact, single-
    unit cards, never a multi-paragraph article - unlike a regular story, there's no benefit to
    letting one flow across a page break, only the risk of a heading/small-card fragment being
    stranded away from the rest of it (see storyprovider/comic.py's short_form comment for the
    concrete case this fixes). article > h1's own `break-after: avoid` above is a same-side hint
    only, and isn't always strong enough on its own once the following block is tall relative to
    the page. */
    article.story-short {{
        page-break-inside: avoid;
    }}

    /* Computed per page_profile/font_size in _comic_image_max_height_in() - not a flat guess -
    so a strip scaled to this height always leaves room for its own headline above it on a fresh
    page. Lives here (not in storyprovider/comic.py's own inline _COMIC_CSS) because only this
    module ever knows the active page_profile/font_size; comic.py's Story is constructed without
    either. width:auto alongside (not height:auto) keeps this from forcing every image up to
    this height - only strips whose natural scaled height would otherwise exceed it are capped. */
    .comic-strip-body img.comic-strip {{
        max-height: {comic_image_max_height_in:.2f}in;
        width: auto;
        height: auto;
    }}

    article.story-short > .story-headline {{
        font-size: {_STORY_SHORT_HEADLINE_FONT_SIZE_EM}em;
        line-height: {_STORY_SHORT_HEADLINE_LINE_HEIGHT};
        margin-bottom: {_STORY_SHORT_HEADLINE_MARGIN_BOTTOM_REM}rem;
    }}

    .sidebar article.story-short > .story-headline {{
        font-size: 0.96em;
    }}

    .story-body > :first-child {{
        margin-top: 0;
    }}

    .story-body > :last-child {{
        margin-bottom: 0;
    }}

    .ear article {{
        margin: 0;
        padding: 0.75rem 0.85rem;
    }}

    .ear article h1 {{
        margin-bottom: 0.2rem;
    }}

    .ear .byline {{
        display: none;
    }}

    .ear .story-body {{
        text-align: center;
    }}

    .ear .story-body p {{
        margin: 0.2rem 0;
    }}

    .ear .story-body p:first-child {{
        font-size: 1.15em;
    }}
    """


def _body_font_override_css(body_font: str) -> str:
    return f"""
    body,
    article,
    .stories,
    .story-body {{
        font-family: {_font_stack(body_font)} !important;
    }}
    """


def _font_stack(override: str | None, fallback: str = "serif") -> str:
    if not override:
        return fallback
    cleaned = override.strip()
    if not cleaned:
        return fallback
    if "," in cleaned:
        return cleaned
    if cleaned.startswith('"') or cleaned.startswith("'"):
        return f"{cleaned}, serif"
    return f'"{cleaned}", serif'
