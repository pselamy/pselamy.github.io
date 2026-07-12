from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import socket
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from unittest import mock


MODULE_PATH = Path(__file__).with_name("check-rendered-agent-fleets.py")
SPEC = importlib.util.spec_from_file_location("check_rendered_agent_fleets", MODULE_PATH)
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class CheckRenderedAgentFleetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.public = Path(self.directory.name)
        section = self.public / "agent-fleets"
        (section / "01-operating-model").mkdir(parents=True)
        (section / "02-tax-and-authority").mkdir()
        (section / "03-skills-and-context-routing").mkdir()
        (section / "05-throughput-and-supersession").mkdir()
        (section / "06-memory-and-provenance").mkdir()
        (section / "07-agent-portfolio").mkdir()
        (section / "diagrams").mkdir()
        (section / "editorial").mkdir()
        (section / "editorial" / "field-guide-hero.png").write_bytes(b"synthetic")
        self.hero_digest = hashlib.sha256(b"synthetic").hexdigest()
        self.manifest = self.public / "editorial-manifest.json"
        for name in ("one.light.svg", "one.dark.svg", "two.light.svg", "two.dark.svg"):
            (section / "diagrams" / name).write_text(
                '<svg aria-labelledby="t d" aria-roledescription="diagram"><title id="t">Title</title><desc id="d">Description</desc></svg>',
                encoding="utf-8",
            )
        hero_alt = "An abstract editorial hero with bounded nodes, two luminous loops, and quiet title space on the left."
        (section / "index.html").write_text(
            '<link rel="canonical" href="https://example.test/agent-fleets/">'
            f'<img class="agent-fleet-hero-image" src="editorial/field-guide-hero.png" width="1536" height="1024" data-asset-id="editorial.field-guide-hero" data-asset-sha256="{self.hero_digest}" alt="{hero_alt}">'
            f'<figcaption class="agent-fleet-hero-caption">{check.HERO_CAPTION}</figcaption>',
            encoding="utf-8",
        )
        self.manifest.write_text(json.dumps({"assets": [{
            "id": "editorial.field-guide-hero", "alt_text": hero_alt,
            "width": 1536, "height": 1024, "sha256": self.hero_digest,
        }]}), encoding="utf-8")
        (section / "01-operating-model" / "index.html").write_text(
            '<link rel="canonical" href="https://example.test/agent-fleets/01-operating-model/">',
            encoding="utf-8",
        )
        (section / "02-tax-and-authority" / "index.html").write_text(
            '<link rel="canonical" href="https://example.test/agent-fleets/02-tax-and-authority/">',
            encoding="utf-8",
        )
        alt = "A sufficiently detailed synthetic description of the diagram for a reader."
        body = '<link rel="canonical" href="https://example.test/agent-fleets/03-skills-and-context-routing/">'
        for stem in ("one", "two"):
            body += f'<img class="agent-fleet-diagram-light" src="../diagrams/{stem}.light.svg" alt="{alt}">'
            body += f'<img class="agent-fleet-diagram-dark" src="../diagrams/{stem}.dark.svg" alt="" aria-hidden="true">'
            body += f'<a class="agent-fleet-diagram-open agent-fleet-diagram-open-light" href="../diagrams/{stem}.light.svg">Open full-size diagram</a>'
            body += f'<a class="agent-fleet-diagram-open agent-fleet-diagram-open-dark" href="../diagrams/{stem}.dark.svg">Open full-size dark diagram</a>'
        (section / "03-skills-and-context-routing" / "index.html").write_text(body, encoding="utf-8")
        (section / "05-throughput-and-supersession" / "index.html").write_text(
            '<link rel="canonical" href="https://example.test/agent-fleets/05-throughput-and-supersession/">',
            encoding="utf-8",
        )
        (section / "06-memory-and-provenance" / "index.html").write_text(
            '<link rel="canonical" href="https://example.test/agent-fleets/06-memory-and-provenance/">',
            encoding="utf-8",
        )
        (section / "07-agent-portfolio" / "index.html").write_text(
            '<link rel="canonical" href="https://example.test/agent-fleets/07-agent-portfolio/">',
            encoding="utf-8",
        )

    def test_valid_fixture(self) -> None:
        result = check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.assertEqual(result, {"html_pages": 7, "canonicals": 7, "diagram_images": 4, "diagram_links": 4, "svg_assets": 4, "hero_images": 1, "external_urls": 0, "external_urls_covered_by_verified_endpoint": 0, "external_endpoints_verified": 0, "external_urls_covered_by_transient_endpoint": 0, "external_endpoints_transient": 0})

    def test_missing_hero_disclaimer_and_alt_fail(self) -> None:
        index = self.public / "agent-fleets" / "index.html"
        index.write_text(index.read_text().replace("Editorial metaphor, not system architecture", "Generic caption"), encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "topology disclaimer"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.setUp()
        index = self.public / "agent-fleets" / "index.html"
        index.write_text(index.read_text().replace("An abstract editorial hero with bounded nodes, two luminous loops, and quiet title space on the left.", "short"), encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "differs from pinned provenance"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)

    def test_machine_marker_and_broken_link_fail(self) -> None:
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        chapter.write_text(chapter.read_text() + "[@evidence:artifact.synthetic]", encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "marker leaked"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)
        chapter.write_text('<link rel="canonical" href="https://example.test/agent-fleets/03-skills-and-context-routing/"><a href="missing/">Missing</a>', encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "broken local"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)

    def test_wrong_canonical_host_or_path_fails(self) -> None:
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        for wrong in ("https://wrong.test/agent-fleets/03-skills-and-context-routing/", "https://example.test/agent-fleets/wrong/"):
            original = chapter.read_text(encoding="utf-8")
            chapter.write_text(original.replace("https://example.test/agent-fleets/03-skills-and-context-routing/", wrong), encoding="utf-8")
            with self.assertRaisesRegex(check.RenderedSiteError, "canonical URL differs"):
                check.check_rendered(self.public, "https://example.test/", self.manifest)
            chapter.write_text(original, encoding="utf-8")

    def test_known_paginator_alias_has_section_canonical(self) -> None:
        alias = self.public / "agent-fleets" / "page" / "1" / "index.html"
        alias.parent.mkdir(parents=True)
        alias.write_text('<link rel="canonical" href="https://example.test/agent-fleets/">', encoding="utf-8")
        result = check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.assertEqual(result["html_pages"], 8)
        alias.write_text('<link rel="canonical" href="https://example.test/agent-fleets/page/1/">', encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "canonical URL differs"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)

    def test_external_url_inventory_and_reachability(self) -> None:
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        chapter.write_text(chapter.read_text(encoding="utf-8") + '<a href="https://github.com/example/path#section">Docs</a>', encoding="utf-8")
        result = check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.assertEqual(result["external_urls"], 1)
        allowed = frozenset({"docs.example.test"})
        self.assertEqual(check.external_url("https://example.test/", "https://docs.example.test/path#section", allowed_hosts=allowed), "https://docs.example.test/path")
        self.assertIsNone(check.external_url("https://example.test/", "/local/"))
        for unsafe in (
            "https://user:pass@docs.example.test/",
            "https://docs.example.test/?access_token=synthetic",
            "https://docs.example.test/?X-Amz-Signature=synthetic",
            "https://docs.example.test/?public=ghp%5FAAAAAAAAAAAAAAAAAAAAAAAA",
            "https://docs.example.test/ghp%5FAAAAAAAAAAAAAAAAAAAAAAAA",
            "http://docs.example.test/path",
            "http://example.test/same-origin",
            "https://docs.example.test:444/path",
            "https://unlisted.example.test/path",
        ):
            with self.assertRaises(check.RenderedSiteError):
                check.external_url("https://example.test/", unsafe, allowed_hosts=allowed)

        chapter.write_text(
            chapter.read_text(encoding="utf-8") + '<a href="/agent-fleets/?access_token=synthetic">Local</a>',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(check.RenderedSiteError, "credential-like"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)

    def test_broken_local_diagnostic_is_redacted(self) -> None:
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        raw = "missing/?public=do-not-echo"
        chapter.write_text(chapter.read_text(encoding="utf-8") + f'<a href="{raw}">Missing</a>', encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "broken local") as raised:
            check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.assertNotIn("do-not-echo", str(raised.exception))
        self.assertIn("sha256=", str(raised.exception))
        allowed = frozenset({"docs.example.test"})

        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return None
            def getcode(self): return 204
            headers = {}

        public_resolver = lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        self.assertEqual(check.check_external_urls(
            {"https://docs.example.test/path"}, opener=lambda *_args, **_kwargs: Response(),
            allowed_hosts=allowed, resolver=public_resolver,
        ), (1, 1, 0, 0))
        for failure in (
            HTTPError("https://docs.example.test/missing", 404, "missing", {}, None),
            URLError("unreachable"),
        ):
            with self.assertRaisesRegex(check.RenderedSiteError, "broken external") as raised:
                check.check_external_urls(
                    {"https://docs.example.test/path?public=value"}, opener=mock.Mock(side_effect=failure),
                    allowed_hosts=allowed, resolver=public_resolver,
                )
            self.assertNotIn("public=value", str(raised.exception))
        self.assertEqual(
            check.check_external_urls(
                {"https://docs.example.test/protected"},
                opener=mock.Mock(side_effect=[
                    HTTPError("https://docs.example.test/protected", 403, "protected", {}, None), Response(),
                ]),
                allowed_hosts=allowed,
                resolver=public_resolver,
            ),
            (1, 1, 0, 0),
        )

    def test_external_checks_deduplicate_query_variants_by_endpoint(self) -> None:
        allowed = frozenset({"docs.example.test"})
        public_resolver = lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        class Response:
            headers = {}
            def __enter__(self): return self
            def __exit__(self, *_): return None
            def getcode(self): return 200
        opener = mock.Mock(return_value=Response())
        result = check.check_external_urls(
            {"https://docs.example.test/share?item=one", "https://docs.example.test/share?item=two"},
            opener=opener, allowed_hosts=allowed, resolver=public_resolver,
        )
        self.assertEqual(result, (2, 1, 0, 0))
        self.assertEqual(opener.call_count, 1)

    def test_rate_limit_is_reported_as_transient_not_verified(self) -> None:
        allowed = frozenset({"news.ycombinator.com"})
        public_resolver = lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        rate_limited = HTTPError("https://news.ycombinator.com/submitlink", 429, "limited", {}, None)
        result = check.check_external_urls(
            {"https://news.ycombinator.com/submitlink?item=one", "https://news.ycombinator.com/submitlink?item=two"},
            opener=mock.Mock(side_effect=rate_limited), allowed_hosts=allowed, resolver=public_resolver,
        )
        self.assertEqual(result, (0, 0, 2, 1))
        with self.assertRaisesRegex(check.RenderedSiteError, "broken external"):
            check.check_external_urls(
                {"https://news.ycombinator.com/article"},
                opener=mock.Mock(side_effect=rate_limited), allowed_hosts=allowed, resolver=public_resolver,
            )

    def test_external_network_policy_blocks_private_resolution_and_redirects(self) -> None:
        allowed = frozenset({"docs.example.test", "localhost"})
        private_resolver = lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]
        with self.assertRaisesRegex(check.RenderedSiteError, "broken external"):
            check.check_external_urls(
                {"https://docs.example.test/path"}, opener=mock.Mock(),
                allowed_hosts=allowed, resolver=private_resolver,
            )
        public_resolver = lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        redirect = HTTPError(
            "https://docs.example.test/path", 302, "redirect",
            {"Location": "https://localhost/private"}, None,
        )
        with self.assertRaisesRegex(check.RenderedSiteError, "broken external"):
            check.check_external_urls(
                {"https://docs.example.test/path"}, opener=mock.Mock(side_effect=redirect),
                allowed_hosts=allowed, resolver=public_resolver,
            )
        missing_location = HTTPError(
            "https://docs.example.test/path", 302, "redirect", {}, None,
        )
        with self.assertRaisesRegex(check.RenderedSiteError, "broken external"):
            check.check_external_urls(
                {"https://docs.example.test/path"}, opener=mock.Mock(side_effect=missing_location),
                allowed_hosts=allowed, resolver=public_resolver,
            )

    def test_parser_inventories_url_bearing_attributes(self) -> None:
        parser = check.PageParser()
        parser.feed('''
            <iframe src="https://github.com/frame"></iframe>
            <video poster="https://github.com/poster"><source srcset="https://github.com/a 1x, https://github.com/b 2x"></video>
            <object data="https://github.com/object"></object>
            <form action="https://github.com/form"><button formaction="https://github.com/button"></button></form>
            <blockquote cite="https://github.com/cite"></blockquote>
            <meta http-equiv="refresh" content="0; url=https://github.com/refresh">
            <meta property="og:image" content="https://github.com/image">
        ''')
        labels = {label for label, _ in parser.links}
        self.assertTrue({
            "iframe@src", "video@poster", "source@srcset", "object@data",
            "form@action", "button@formaction", "blockquote@cite",
            "meta@refresh", "meta@og:image",
        }.issubset(labels))

    def test_missing_alt_and_accessible_svg_fail(self) -> None:
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        chapter.write_text(chapter.read_text().replace("A sufficiently detailed synthetic description of the diagram for a reader.", "short", 1), encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "useful alt"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.setUp()
        svg = self.public / "agent-fleets" / "diagrams" / "one.light.svg"
        svg.write_text("<svg/>", encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "SVG lacks"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)

    def test_missing_page_canonical_dark_duplicate_and_full_size_links_fail(self) -> None:
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        chapter.unlink()
        with self.assertRaisesRegex(check.RenderedSiteError, "missing required"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.setUp()
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        chapter.write_text(chapter.read_text().replace('rel="canonical"', 'rel="alternate"'), encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "one canonical"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.setUp()
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        chapter.write_text(chapter.read_text().replace('alt="" aria-hidden="true"', 'alt="duplicate" aria-hidden="false"', 1), encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "hidden from assistive"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)
        self.setUp()
        chapter = self.public / "agent-fleets" / "03-skills-and-context-routing" / "index.html"
        chapter.write_text(chapter.read_text().replace("agent-fleet-diagram-open", "removed-open-link"), encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "full-size links"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)

    def test_target_resolution_and_cli(self) -> None:
        self.assertIsNone(check.target_for(self.public, "https://example.test/", "https://example.test/page/", "https://other.test/x"))
        target = check.target_for(self.public, "https://example.test/base/", "https://example.test/base/agent-fleets/", "../favicon.svg")
        self.assertEqual(target, (self.public / "favicon.svg").resolve())
        outside = self.public.parent / f"{self.public.name}-outside.txt"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        traversal = f"https://example.test/%2e%2e/{outside.name}"
        with self.assertRaisesRegex(check.RenderedSiteError, "escapes"):
            check.target_for(self.public, "https://example.test/", "https://example.test/agent-fleets/", traversal)
        symlink = self.public / "escape.txt"
        symlink.symlink_to(outside)
        with self.assertRaisesRegex(check.RenderedSiteError, "escapes"):
            check.target_for(self.public, "https://example.test/", "https://example.test/agent-fleets/", "/escape.txt")
        stdout = io.StringIO()
        with mock.patch("sys.argv", ["check", "--public", str(self.public), "--base-url", "https://example.test/", "--editorial-manifest", str(self.manifest)]), mock.patch("sys.stdout", stdout):
            self.assertEqual(check.main(), 0)
        self.assertIn("rendered field-guide check passed", stdout.getvalue())
        stderr = io.StringIO()
        with mock.patch("sys.argv", ["check", "--public", str(self.public / "missing")]), mock.patch("sys.stderr", stderr):
            self.assertEqual(check.main(), 1)
        self.assertIn("rendered field-guide check failed", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
