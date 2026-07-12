#!/usr/bin/env python3
"""Validate the unpublished field-guide HTML, assets, and bounded link graph.

The network check uses an exact HTTPS-host allowlist, disables automatic
redirects, and rejects non-public DNS answers. The standard-library transport
does not pin the preflight DNS answer to the later TLS connection, so this is
not a cryptographic defense against DNS rebinding; the fixed reputable-host
allowlist is the additional boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import html.parser
import ipaddress
import json
import re
import socket
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, unquote, urldefrag, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


class RenderedSiteError(ValueError):
    """The rendered field-guide preview violates its site contract."""


class PageParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.canonicals: list[str] = []
        self.diagram_images: list[dict[str, str]] = []
        self.diagram_links: list[dict[str, str]] = []
        self.hero_images: list[dict[str, str]] = []
        self.hero_caption = ""
        self._in_hero_caption = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        url_attrs = {
            "a": ("href",), "area": ("href",), "link": ("href",),
            "img": ("src", "srcset"), "script": ("src",), "source": ("src", "srcset"),
            "iframe": ("src",), "video": ("src", "poster"), "audio": ("src",),
            "track": ("src",), "embed": ("src",), "object": ("data",),
            "form": ("action",), "button": ("formaction",), "input": ("formaction",),
            "blockquote": ("cite",), "q": ("cite",), "del": ("cite",), "ins": ("cite",),
        }
        for attribute in url_attrs.get(tag, ()):
            raw = values.get(attribute)
            if not raw:
                continue
            if attribute == "srcset":
                for candidate in raw.split(","):
                    url = candidate.strip().split(maxsplit=1)[0]
                    if url:
                        self.links.append((f"{tag}@{attribute}", url))
            else:
                self.links.append((f"{tag}@{attribute}", raw))
        if tag == "meta":
            if values.get("http-equiv", "").lower() == "refresh":
                match = re.search(r"(?i)(?:^|;)\s*url\s*=\s*([^;]+)", values.get("content", ""))
                if match:
                    self.links.append(("meta@refresh", match.group(1).strip(" \"'")))
            key = (values.get("property") or values.get("name", "")).lower()
            if key in {"og:url", "og:image", "og:video", "og:audio", "twitter:url", "twitter:image"} and values.get("content"):
                self.links.append((f"meta@{key}", values["content"]))
        if tag == "link" and "canonical" in values.get("rel", "").split():
            self.canonicals.append(values.get("href", ""))
        if tag == "img" and "agent-fleet-diagram" in values.get("class", ""):
            self.diagram_images.append(values)
        if tag == "a" and "agent-fleet-diagram-open" in values.get("class", ""):
            self.diagram_links.append(values)
        if tag == "img" and values.get("class") == "agent-fleet-hero-image":
            self.hero_images.append(values)
        if tag == "figcaption" and values.get("class") == "agent-fleet-hero-caption":
            self._in_hero_caption = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "figcaption":
            self._in_hero_caption = False

    def handle_data(self, data: str) -> None:
        if self._in_hero_caption:
            self.hero_caption += data


def target_for(public: Path, base_url: str, page_url: str, raw: str) -> Path | None:
    parsed = urlparse(raw)
    if raw.startswith(("mailto:", "tel:", "#", "//")):
        return None
    resolved = urlparse(urljoin(page_url, raw))
    if resolved.scheme not in {"http", "https"} or resolved.netloc != urlparse(base_url).netloc:
        return None
    base_path = urlparse(base_url).path.rstrip("/")
    path = unquote(resolved.path)
    if base_path and path.startswith(base_path + "/"):
        path = path[len(base_path):]
    relative = path.lstrip("/")
    target = public / relative
    if path.endswith("/") or not target.suffix:
        target = target / "index.html"
    public_root = public.resolve()
    resolved_target = target.resolve(strict=False)
    if not resolved_target.is_relative_to(public_root):
        raise RenderedSiteError("local URL escapes the rendered public root")
    return resolved_target


EXTERNAL_HOSTS = frozenset({
    "api.whatsapp.com", "facebook.com", "www.facebook.com", "github.com", "gohugo.io",
    "news.ycombinator.com", "reddit.com", "www.reddit.com", "selamy.dev", "speedforge.dev", "telegram.me",
    "www.linkedin.com", "x.com",
})
SENSITIVE_QUERY_KEYS = frozenset({
    "access_token", "api_key", "apikey", "auth", "authorization", "credential",
    "expires", "key", "password", "secret", "sig", "signature", "token",
})
TOKEN_VALUE = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})"
)
INTERACTION_ENDPOINTS = frozenset({
    ("api.whatsapp.com", "/send"),
    ("facebook.com", "/sharer/sharer.php"),
    ("news.ycombinator.com", "/submitlink"),
    ("reddit.com", "/submit"),
    ("telegram.me", "/share/url"),
    ("www.linkedin.com", "/shareArticle"),
    ("x.com", "/intent/tweet/"),
})


def _decoded_variants(value: str, rounds: int = 2) -> tuple[str, ...]:
    values = [value]
    for _ in range(rounds):
        decoded = unquote(values[-1])
        if decoded == values[-1]:
            break
        values.append(decoded)
    return tuple(values)


def _validate_url_material(resolved: str) -> None:
    if len(resolved) > 8192:
        raise RenderedSiteError("URL exceeds the reviewable length limit")
    parsed = urlparse(resolved)
    if parsed.scheme in {"http", "https"} and parsed.scheme != "https":
        raise RenderedSiteError("HTTP URL is not allowed")
    query = parse_qsl(parsed.query, keep_blank_values=True)
    query_keys = {key.lower().replace("-", "_") for key, _ in query}
    sensitive_query = any(
        key in SENSITIVE_QUERY_KEYS
        or key.startswith("x_amz_")
        or key.endswith(("_token", "_secret", "_password", "_signature", "_credential", "_key"))
        for key in query_keys
    )
    material = [resolved, parsed.path, parsed.fragment, parsed.username or "", parsed.password or ""]
    material.extend(value for _, value in query)
    if sensitive_query or any(TOKEN_VALUE.search(candidate) for value in material for candidate in _decoded_variants(value)):
        raise RenderedSiteError("URL contains credential-like material")


def external_url(base_url: str, raw: str, *, allowed_hosts: frozenset[str] = EXTERNAL_HOSTS) -> str | None:
    resolved = urljoin(base_url, raw)
    _validate_url_material(resolved)
    parsed = urlparse(resolved)
    if parsed.scheme not in {"http", "https"} or parsed.netloc == urlparse(base_url).netloc:
        return None
    host = (parsed.hostname or "").lower()
    try:
        port = parsed.port
    except ValueError as exc:
        raise RenderedSiteError("external URL contains an invalid port") from exc
    if parsed.scheme != "https" or port not in {None, 443} or not host or host not in allowed_hosts:
        raise RenderedSiteError("external URL violates the HTTPS host allowlist")
    if parsed.username or parsed.password:
        raise RenderedSiteError("external URL contains credential-like material")
    return urldefrag(resolved).url


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _public_target(url: str, *, allowed_hosts: frozenset[str], resolver=socket.getaddrinfo) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    try:
        port = parsed.port
    except ValueError as exc:
        raise RenderedSiteError("external URL contains an invalid port") from exc
    if parsed.scheme != "https" or port not in {None, 443} or host not in allowed_hosts:
        raise RenderedSiteError("external redirect violates the HTTPS host allowlist")
    try:
        addresses = resolver(host, port or 443, type=socket.SOCK_STREAM)
    except Exception as exc:
        raise RenderedSiteError("external hostname resolution failed; value redacted") from exc
    if not addresses:
        raise RenderedSiteError("external hostname resolved to no addresses")
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address[4][0])
        except (IndexError, ValueError) as exc:
            raise RenderedSiteError("external hostname returned an invalid address") from exc
        if not ip.is_global:
            raise RenderedSiteError("external hostname resolves outside the public Internet")


def _url_label(url: str) -> str:
    host = (urlparse(url).hostname or "unknown").lower()
    return f"host={host} sha256={hashlib.sha256(url.encode()).hexdigest()[:16]}"


def _request_status(
    url: str,
    *,
    method: str,
    timeout: float,
    opener,
    allowed_hosts: frozenset[str],
    resolver,
    max_redirects: int = 5,
) -> int:
    current = url
    for _ in range(max_redirects + 1):
        _public_target(current, allowed_hosts=allowed_hosts, resolver=resolver)
        headers = {"User-Agent": "operating-agent-fleets-link-check/1"}
        if method == "GET":
            headers["Range"] = "bytes=0-0"
        request = Request(current, method=method, headers=headers)
        try:
            with opener(request, timeout=timeout) as response:
                status = response.getcode()
                location = response.headers.get("Location") if getattr(response, "headers", None) else None
        except HTTPError as exc:
            status = exc.code
            location = exc.headers.get("Location") if exc.headers else None
        if 300 <= status < 400:
            if status not in {301, 302, 303, 307, 308} or not location:
                raise RenderedSiteError("external URL returned an unusable redirect")
            candidate = urljoin(current, location)
            current = external_url("https://selamy.dev/", candidate, allowed_hosts=allowed_hosts)
            if current is None:
                raise RenderedSiteError("external redirect target is invalid")
            continue
        return status
    raise RenderedSiteError("external URL exceeded the redirect limit")


def check_external_urls(
    urls: set[str],
    *,
    timeout: float = 10.0,
    opener=None,
    allowed_hosts: frozenset[str] = EXTERNAL_HOSTS,
    resolver=socket.getaddrinfo,
) -> tuple[int, int, int, int]:
    opener = opener or build_opener(NoRedirect).open
    failures: list[str] = []
    endpoints: dict[tuple[str, str, str], list[str]] = {}
    for url in sorted(urls):
        parsed = urlparse(url)
        endpoints.setdefault((parsed.scheme, parsed.netloc, parsed.path), []).append(url)
    verified_urls = 0
    verified_endpoints = 0
    transient_urls = 0
    transient_endpoints = 0
    for variants in endpoints.values():
        url = variants[0]
        try:
            status = _request_status(
                url, method="HEAD", timeout=timeout, opener=opener,
                allowed_hosts=allowed_hosts, resolver=resolver,
            )
            if status in {403, 405}:
                status = _request_status(
                    url, method="GET", timeout=timeout, opener=opener,
                    allowed_hosts=allowed_hosts, resolver=resolver,
                )
            endpoint = ((urlparse(url).hostname or "").lower(), urlparse(url).path)
            if status in {401, 403, 429} and endpoint in INTERACTION_ENDPOINTS:
                transient_urls += len(variants)
                transient_endpoints += 1
            elif status is None or not 200 <= status < 300:
                failures.append(f"{_url_label(url)} status={status}")
            else:
                verified_urls += len(variants)
                verified_endpoints += 1
        except Exception:
            failures.append(f"{_url_label(url)} request-failed")
    if failures:
        raise RenderedSiteError("broken external references:\n" + "\n".join(failures))
    return verified_urls, verified_endpoints, transient_urls, transient_endpoints


HERO_CAPTION = "Editorial metaphor, not system architecture: the nodes, loops, gateways, and central ledger do not represent deployed topology, direct peer connectivity, central orchestration, or a verified agent count."


def expected_canonical(base_url: str, page_relative: Path) -> str:
    if page_relative == Path("agent-fleets/page/1/index.html"):
        return urljoin(base_url, "/agent-fleets/")
    return urljoin(base_url, "/" + str(page_relative.parent) + "/")


def check_rendered(
    public: Path,
    base_url: str,
    editorial_manifest: Path | None = None,
    *,
    check_external: bool = False,
) -> dict[str, int]:
    section = public / "agent-fleets"
    required = [
        section / "index.html",
        section / "01-operating-model" / "index.html",
        section / "02-tax-and-authority" / "index.html",
        section / "03-skills-and-context-routing" / "index.html",
        section / "05-throughput-and-supersession" / "index.html",
        section / "06-memory-and-provenance" / "index.html",
        section / "07-agent-portfolio" / "index.html",
    ]
    missing_required = [str(path.relative_to(public)) for path in required if not path.is_file()]
    if missing_required:
        raise RenderedSiteError(f"missing required rendered pages: {', '.join(missing_required)}")

    html_files = sorted(section.rglob("*.html"))
    broken: set[str] = set()
    canonical_count = 0
    diagrams = []
    diagram_links = []
    hero_images = []
    hero_captions = []
    external_urls: set[str] = set()
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if "[@evidence:" in text:
            raise RenderedSiteError(f"machine evidence marker leaked into {path.relative_to(public)}")
        parser = PageParser()
        parser.feed(text)
        page_relative = path.relative_to(public)
        page_path = "/" + str(page_relative.parent) + "/"
        page_url = urljoin(base_url, page_path)
        if len(parser.canonicals) != 1:
            raise RenderedSiteError(f"expected one canonical URL in {page_relative}")
        if parser.canonicals[0] != expected_canonical(base_url, page_relative):
            raise RenderedSiteError(
                f"canonical URL differs from rendered page URL in {page_relative}"
            )
        canonical_count += 1
        for tag, raw in parser.links:
            target = target_for(public, base_url, page_url, raw)
            if target is not None and not target.exists():
                resolved = urljoin(page_url, raw)
                parsed_resolved = urlparse(resolved)
                if urlparse(raw).scheme in {"http", "https"} and parsed_resolved.netloc == urlparse(base_url).netloc:
                    _validate_url_material(resolved)
                    external_urls.add(urldefrag(resolved).url)
                else:
                    raw_digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
                    broken.add(f"{page_relative}: {tag} sha256={raw_digest}")
            external = external_url(base_url, raw)
            if external is not None:
                external_urls.add(external)
        diagrams.extend(parser.diagram_images)
        diagram_links.extend(parser.diagram_links)
        hero_images.extend(parser.hero_images)
        if parser.hero_caption.strip():
            hero_captions.append(parser.hero_caption.strip())
    if broken:
        raise RenderedSiteError("broken local references:\n" + "\n".join(sorted(broken)))
    verified_external, verified_endpoints, transient_external, transient_endpoints = (
        check_external_urls(external_urls) if check_external else (0, 0, 0, 0)
    )

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
    hero_asset = section / "editorial" / "field-guide-hero.png"
    if len(hero_images) != 1 or not hero_asset.is_file():
        raise RenderedSiteError("expected exactly one rendered editorial hero and asset")
    manifest_path = editorial_manifest or public.parent / "data" / "operating-agent-fleets" / "editorial-assets" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = [asset for asset in manifest["assets"] if asset["id"] == "editorial.field-guide-hero"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise RenderedSiteError("cannot resolve pinned editorial hero provenance") from exc
    if len(records) != 1:
        raise RenderedSiteError("pinned editorial manifest must contain exactly one hero record")
    record = records[0]
    hero = hero_images[0]
    actual_digest = hashlib.sha256(hero_asset.read_bytes()).hexdigest()
    if (
        hero.get("alt") != record.get("alt_text")
        or hero.get("width") != str(record.get("width"))
        or hero.get("height") != str(record.get("height"))
        or hero.get("data-asset-id") != record.get("id")
        or hero.get("data-asset-sha256") != record.get("sha256")
        or actual_digest != record.get("sha256")
    ):
        raise RenderedSiteError("editorial hero differs from pinned provenance")
    if len(hero_captions) != 1 or " ".join(hero_captions[0].split()) != HERO_CAPTION:
        raise RenderedSiteError("editorial hero lacks the required topology disclaimer")
    return {
        "html_pages": len(html_files),
        "canonicals": canonical_count,
        "diagram_images": len(diagrams),
        "diagram_links": len(diagram_links),
        "svg_assets": len(list((section / "diagrams").rglob("*.svg"))),
        "hero_images": len(hero_images),
        "external_urls": len(external_urls),
        "external_urls_covered_by_verified_endpoint": verified_external,
        "external_endpoints_verified": verified_endpoints,
        "external_urls_covered_by_transient_endpoint": transient_external,
        "external_endpoints_transient": transient_endpoints,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--base-url", default="https://selamy.dev/")
    parser.add_argument("--editorial-manifest", type=Path)
    parser.add_argument("--check-external", action="store_true")
    args = parser.parse_args()
    try:
        manifest = args.editorial_manifest.resolve() if args.editorial_manifest else None
        result = check_rendered(
            args.public.resolve(),
            args.base_url,
            manifest,
            check_external=args.check_external,
        )
    except (OSError, RenderedSiteError) as exc:
        print(f"rendered field-guide check failed: {exc}", file=sys.stderr)
        return 1
    print("rendered field-guide check passed: " + ", ".join(f"{key}={value}" for key, value in result.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
