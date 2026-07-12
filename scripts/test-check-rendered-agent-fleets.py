from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
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
        self.assertEqual(result, {"html_pages": 7, "canonicals": 7, "diagram_images": 4, "diagram_links": 4, "svg_assets": 4, "hero_images": 1})

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
        chapter.write_text('<link rel="canonical" href="https://example.test/x"><a href="missing/">Missing</a>', encoding="utf-8")
        with self.assertRaisesRegex(check.RenderedSiteError, "broken local"):
            check.check_rendered(self.public, "https://example.test/", self.manifest)

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
        self.assertEqual(target, self.public / "favicon.svg")
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
