#!/usr/bin/env python3
"""Validate the unpublished field-guide HTML and local asset graph."""

from __future__ import annotations

import argparse
import html.parser
import sys
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse


class RenderedSiteError(ValueError):
    """The rendered field-guide preview violates its site contract."""


class PageParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.canonicals: list[str] = []
        self.diagram_images: list[dict[str, str]] = []
        self.diagram_links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag in {"a", "link"} and values.get("href"):
            self.links.append((tag, values["href"]))
        if tag in {"img", "script", "source"} and values.get("src"):
            self.links.append((tag, values["src"]))
        if tag == "link" and "canonical" in values.get("rel", "").split():
            self.canonicals.append(values.get("href", ""))
        if tag == "img" and "agent-fleet-diagram" in values.get("class", ""):
            self.diagram_images.append(values)
        if tag == "a" and "agent-fleet-diagram-open" in values.get("class", ""):
            self.diagram_links.append(values)


def target_for(public: Path, base_url: str, page_url: str, raw: str) -> Path | None:
    parsed = urlparse(raw)
    if parsed.scheme or raw.startswith(("mailto:", "tel:", "#", "//")):
        return None
    resolved = urlparse(urljoin(page_url, raw))
    base_path = urlparse(base_url).path.rstrip("/")
    path = unquote(resolved.path)
    if base_path and path.startswith(base_path + "/"):
        path = path[len(base_path):]
    relative = path.lstrip("/")
    target = public / relative
    if path.endswith("/") or not target.suffix:
        target = target / "index.html"
    return target


def check_rendered(public: Path, base_url: str) -> dict[str, int]:
    section = public / "agent-fleets"
    required = [
        section / "index.html",
        section / "01-operating-model" / "index.html",
        section / "02-tax-and-authority" / "index.html",
        section / "03-skills-and-context-routing" / "index.html",
        section / "05-throughput-and-supersession" / "index.html",
        section / "06-memory-and-provenance" / "index.html",
    ]
    missing_required = [str(path.relative_to(public)) for path in required if not path.is_file()]
    if missing_required:
        raise RenderedSiteError(f"missing required rendered pages: {', '.join(missing_required)}")

    html_files = sorted(section.rglob("*.html"))
    broken: set[str] = set()
    canonical_count = 0
    diagrams = []
    diagram_links = []
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if "[@evidence:" in text:
            raise RenderedSiteError(f"machine evidence marker leaked into {path.relative_to(public)}")
        parser = PageParser()
        parser.feed(text)
        if len(parser.canonicals) != 1:
            raise RenderedSiteError(f"expected one canonical URL in {path.relative_to(public)}")
        canonical_count += 1
        page_relative = path.relative_to(public)
        page_path = "/" + str(page_relative.parent) + "/"
        page_url = urljoin(base_url, page_path)
        for tag, raw in parser.links:
            target = target_for(public, base_url, page_url, raw)
            if target is not None and not target.exists():
                broken.add(f"{page_relative}: {tag} {raw}")
        diagrams.extend(parser.diagram_images)
        diagram_links.extend(parser.diagram_links)
    if broken:
        raise RenderedSiteError("broken local references:\n" + "\n".join(sorted(broken)))

    light = [image for image in diagrams if "diagram-light" in image.get("class", "")]
    dark = [image for image in diagrams if "diagram-dark" in image.get("class", "")]
    light_assets = list((section / "diagrams").rglob("*.light.svg"))
    dark_assets = list((section / "diagrams").rglob("*.dark.svg"))
    if not light_assets or len(light) != len(light_assets) or len(dark) != len(dark_assets):
        raise RenderedSiteError("rendered diagram count differs from exported light and dark assets")
    if any(len(image.get("alt", "").strip()) < 40 for image in light):
        raise RenderedSiteError("light diagram is missing useful alt text")
    if any(image.get("alt") != "" or image.get("aria-hidden") != "true" for image in dark):
        raise RenderedSiteError("dark duplicate must be hidden from assistive technology")
    if len(diagram_links) != len(light_assets) + len(dark_assets) or any(
        not link.get("href") or not link.get("class") for link in diagram_links
    ):
        raise RenderedSiteError("expected theme-aware full-size links for every diagram")

    for svg in sorted((section / "diagrams").rglob("*.svg")):
        text = svg.read_text(encoding="utf-8")
        if not all(marker in text for marker in ("<title", "<desc", "aria-labelledby", "aria-roledescription")):
            raise RenderedSiteError(f"SVG lacks accessible metadata: {svg.relative_to(public)}")
    return {
        "html_pages": len(html_files),
        "canonicals": canonical_count,
        "diagram_images": len(diagrams),
        "diagram_links": len(diagram_links),
        "svg_assets": len(list((section / "diagrams").rglob("*.svg"))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--base-url", default="https://selamy.dev/")
    args = parser.parse_args()
    try:
        result = check_rendered(args.public.resolve(), args.base_url)
    except (OSError, RenderedSiteError) as exc:
        print(f"rendered field-guide check failed: {exc}", file=sys.stderr)
        return 1
    print("rendered field-guide check passed: " + ", ".join(f"{key}={value}" for key, value in result.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
