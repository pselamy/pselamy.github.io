from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).with_name("stage-operating-agent-fleets.py")
SPEC = importlib.util.spec_from_file_location("stage_operating_agent_fleets", MODULE_PATH)
stage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage)


class StageOperatingAgentFleetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def test_load_config_requires_exact_repo_sha_and_counts(self) -> None:
        path = self.root / "config.json"
        valid = {
            "repository": stage.ALLOWED_REPOSITORY,
            "ref": "a" * 40,
            "expected_preview_entries": 3,
            "expected_release_entries": 0,
        }
        path.write_text(json.dumps(valid), encoding="utf-8")
        self.assertEqual(stage.load_config(path), valid)
        for field, value in (("repository", "https://example.com/repo"), ("ref", "main"), ("expected_preview_entries", True)):
            invalid = {**valid, field: value}
            path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.subTest(field=field), self.assertRaises(stage.StagingError):
                stage.load_config(path)
        path.write_text("not json", encoding="utf-8")
        with self.assertRaisesRegex(stage.StagingError, "cannot load"):
            stage.load_config(path)
        path.write_text(json.dumps({**valid, "extra": True}), encoding="utf-8")
        with self.assertRaisesRegex(stage.StagingError, "exactly"):
            stage.load_config(path)

    def test_checkout_source_fetches_exact_local_commit(self) -> None:
        upstream = self.root / "upstream"
        upstream.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=upstream, check=True)
        subprocess.run(["git", "config", "user.name", "Synthetic Test"], cwd=upstream, check=True)
        subprocess.run(["git", "config", "user.email", "synthetic@example.invalid"], cwd=upstream, check=True)
        (upstream / "README.md").write_text("synthetic\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=upstream, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "synthetic"], cwd=upstream, check=True)
        ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=upstream, check=True, capture_output=True, text=True).stdout.strip()
        checkout = stage.checkout_source({"repository": str(upstream), "ref": ref}, self.root / "checkout")
        self.assertEqual(subprocess.run(["git", "rev-parse", "HEAD"], cwd=checkout, check=True, capture_output=True, text=True).stdout.strip(), ref)
        with self.assertRaisesRegex(stage.StagingError, "failed to fetch"):
            stage.checkout_source({"repository": str(upstream), "ref": "0" * 40}, self.root / "bad-checkout")

    def test_run_export_accepts_exact_metadata_and_rejects_mismatch(self) -> None:
        source = self.root / "source"
        (source / "tools").mkdir(parents=True)
        ref = "d" * 40
        script = (
            "import argparse,json,pathlib\n"
            "p=argparse.ArgumentParser(); p.add_argument('--channel'); p.add_argument('--output'); a=p.parse_args()\n"
            "pathlib.Path(a.output).mkdir(parents=True)\n"
            f"print(json.dumps({{'source_revision':'{ref}','source_dirty':False,'requested_channel':a.channel,'entries':[{{}}]}}))\n"
        )
        (source / "tools" / "export_site.py").write_text(script, encoding="utf-8")
        config = {"ref": ref, "expected_preview_entries": 1, "expected_release_entries": 0}
        metadata = stage.run_export(source, self.root / "bundle", "preview", config)
        self.assertEqual(metadata["source_revision"], ref)
        with self.assertRaisesRegex(stage.StagingError, "expected 2"):
            stage.run_export(source, self.root / "bundle-two", "preview", {**config, "expected_preview_entries": 2})
        (source / "tools" / "export_site.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
        with self.assertRaisesRegex(stage.StagingError, "export failed"):
            stage.run_export(source, self.root / "bundle-fail", "preview", config)

    def test_render_content_adds_draft_frontmatter_and_rewrites_evidence_only(self) -> None:
        source = self.root / "chapter.md"
        destination = self.root / "out" / "chapter.md"
        source.write_text(
            "# Chapter title\n\n"
            "[Evidence](../evidence/records/agent-skills.yaml) [@evidence:artifact.public-agent-skills]\n\n"
            "![Diagram](../diagrams/chapter-03/example.light.svg)\n\n"
            "[Exported](03-exported.md) and [Planned](04-planned.md)\n",
            encoding="utf-8",
        )
        stage.render_content(
            source,
            destination,
            ref="b" * 40,
            channel="preview",
            available_content={"03-exported.md"},
        )
        rendered = destination.read_text(encoding="utf-8")
        self.assertIn('title: "Chapter title"', rendered)
        self.assertIn("draft: true", rendered)
        self.assertIn("blob/" + "b" * 40 + "/evidence/records/agent-skills.yaml", rendered)
        self.assertIn("../diagrams/chapter-03/example.light.svg", rendered)
        self.assertIn("[Exported](03-exported/)", rendered)
        self.assertIn("and Planned", rendered)
        self.assertNotIn("04-planned.md", rendered)
        self.assertNotIn("[@evidence:", rendered)
        self.assertNotIn("# Chapter title", rendered)

    def bundle(self) -> tuple[Path, dict]:
        bundle = self.root / "bundle"
        (bundle / "content").mkdir(parents=True)
        (bundle / "content" / "_index.md").write_text("# Map\n\nBody\n", encoding="utf-8")
        (bundle / "data" / "evidence").mkdir(parents=True)
        (bundle / "data" / "evidence" / "manifest.json").write_text("{}\n", encoding="utf-8")
        (bundle / "data" / "editorial-assets").mkdir()
        (bundle / "data" / "editorial-assets" / "manifest.json").write_text('{"assets": []}\n', encoding="utf-8")
        (bundle / "static" / "agent-fleets" / "diagrams").mkdir(parents=True)
        (bundle / "static" / "agent-fleets" / "diagrams" / "sample.svg").write_text("<svg/>\n", encoding="utf-8")
        (bundle / "static" / "agent-fleets" / "editorial").mkdir()
        (bundle / "static" / "agent-fleets" / "editorial" / "field-guide-hero.png").write_bytes(b"synthetic")
        metadata = {"source_revision": "c" * 40, "entries": []}
        return bundle, metadata

    def test_stage_bundle_routes_content_data_static_and_metadata(self) -> None:
        bundle, metadata = self.bundle()
        site = self.root / "site"
        site.mkdir()
        stage.stage_bundle(site, bundle, metadata, ref="c" * 40, channel="preview")
        self.assertTrue((site / "content" / "agent-fleets" / "_index.md").is_file())
        self.assertTrue((site / "data" / "operating-agent-fleets" / "evidence" / "manifest.json").is_file())
        self.assertTrue((site / "data" / "operating-agent-fleets" / "editorial-assets" / "manifest.json").is_file())
        self.assertTrue((site / "static" / "agent-fleets" / "diagrams" / "sample.svg").is_file())
        self.assertIn("{{< agent-fleet-hero >}}", (site / "content" / "agent-fleets" / "_index.md").read_text())
        stored = json.loads((site / "data" / "operating-agent-fleets" / "export-metadata.json").read_text())
        self.assertEqual(stored, metadata)

    def test_stage_bundle_refuses_existing_managed_target(self) -> None:
        bundle, metadata = self.bundle()
        site = self.root / "site"
        (site / "content" / "agent-fleets").mkdir(parents=True)
        with self.assertRaisesRegex(stage.StagingError, "already exist"):
            stage.stage_bundle(site, bundle, metadata, ref="c" * 40, channel="preview")

    def test_stage_bundle_refuses_partial_editorial_hero(self) -> None:
        bundle, metadata = self.bundle()
        (bundle / "data" / "editorial-assets" / "manifest.json").unlink()
        with self.assertRaisesRegex(stage.StagingError, "must be exported together"):
            stage.stage_bundle(self.root / "site-missing-manifest", bundle, metadata, ref="c" * 40, channel="preview")
        shutil.rmtree(bundle)
        bundle, metadata = self.bundle()
        (bundle / "static" / "agent-fleets" / "editorial" / "field-guide-hero.png").unlink()
        with self.assertRaisesRegex(stage.StagingError, "must be exported together"):
            stage.stage_bundle(self.root / "site-missing-image", bundle, metadata, ref="c" * 40, channel="preview")

    def test_main_reports_success_and_failure(self) -> None:
        config = {
            "repository": stage.ALLOWED_REPOSITORY,
            "ref": "e" * 40,
            "expected_preview_entries": 0,
            "expected_release_entries": 0,
        }
        stdout = io.StringIO()
        with mock.patch("sys.argv", ["stage", "--site-root", str(self.root / "site")]), \
             mock.patch.object(stage, "load_config", return_value=config), \
             mock.patch.object(stage, "checkout_source", return_value=self.root), \
             mock.patch.object(stage, "run_export", return_value={"entries": []}), \
             mock.patch.object(stage, "stage_bundle"), \
             mock.patch("sys.stdout", stdout):
            self.assertEqual(stage.main(), 0)
        self.assertIn(config["ref"], stdout.getvalue())
        stderr = io.StringIO()
        with mock.patch("sys.argv", ["stage", "--site-root", str(self.root / "site")]), \
             mock.patch.object(stage, "load_config", side_effect=stage.StagingError("synthetic")), \
             mock.patch("sys.stderr", stderr):
            self.assertEqual(stage.main(), 1)
        self.assertIn("field-guide staging failed", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
