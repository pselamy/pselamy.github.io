#!/usr/bin/env python3
"""Stage a pinned, allowlisted Operating Agent Fleets export into Hugo."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SITE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = SITE_ROOT / "data" / "operating-agent-fleets-source.json"
ALLOWED_REPOSITORY = "https://github.com/pselamy/operating-agent-fleets.git"
SHA = re.compile(r"^[0-9a-f]{40}$")
EVIDENCE_LINK = re.compile(r"\(\.\./evidence/records/([a-z0-9-]+\.yaml)\)")
CITATION_MARKER = re.compile(r"\s*\[@evidence:[a-z][a-z0-9-]*(?:\.[a-z0-9][a-z0-9-]*)+\]")
GUIDE_LINK = re.compile(r"\[([^\]]+)\]\(([0-9]{2}-[a-z0-9-]+)\.md\)")
TARGETS = {
    "content": Path("content/agent-fleets"),
    "data": Path("data/operating-agent-fleets"),
    "static": Path("static/agent-fleets"),
}


class StagingError(ValueError):
    """Pinned-source staging failed its integrity or publication checks."""


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StagingError(f"cannot load source config: {exc}") from exc
    fields = {"repository", "ref", "expected_preview_entries", "expected_release_entries"}
    if not isinstance(config, dict) or set(config) != fields:
        raise StagingError(f"source config must contain exactly {sorted(fields)}")
    if config["repository"] != ALLOWED_REPOSITORY or SHA.fullmatch(config["ref"]) is None:
        raise StagingError("repository or immutable ref is not allowlisted")
    for field in ("expected_preview_entries", "expected_release_entries"):
        if not isinstance(config[field], int) or isinstance(config[field], bool) or config[field] < 0:
            raise StagingError(f"{field} must be a non-negative integer")
    return config


def checkout_source(config: dict[str, Any], destination: Path) -> Path:
    destination.mkdir(parents=True)
    commands = (
        ["git", "init", "--quiet"],
        ["git", "remote", "add", "origin", config["repository"]],
        ["git", "fetch", "--quiet", "--depth=1", "origin", config["ref"]],
        ["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"],
    )
    try:
        for command in commands:
            subprocess.run(command, cwd=destination, check=True)
        actual = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=destination, check=True, capture_output=True, text=True
        ).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise StagingError("failed to fetch the pinned field-guide revision") from exc
    if actual != config["ref"]:
        raise StagingError(f"fetched revision mismatch: expected {config['ref']}, got {actual}")
    return destination


def run_export(source: Path, bundle: Path, channel: str, config: dict[str, Any]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [sys.executable, "tools/export_site.py", "--channel", channel, "--output", str(bundle)],
            cwd=source,
            check=True,
            capture_output=True,
            text=True,
        )
        metadata = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise StagingError("pinned field-guide export failed") from exc
    expected = config[f"expected_{channel}_entries"]
    if metadata.get("source_revision") != config["ref"] or metadata.get("source_dirty") is not False:
        raise StagingError("export metadata does not identify the clean pinned revision")
    if metadata.get("requested_channel") != channel or len(metadata.get("entries", [])) != expected:
        raise StagingError(f"export entry count or channel differs from config; expected {expected}")
    return metadata


def _title_and_body(text: str, fallback: str) -> tuple[str, str]:
    lines = text.splitlines()
    title = fallback
    if lines and lines[0].startswith("# "):
        title = lines.pop(0)[2:].strip()
        while lines and not lines[0].strip():
            lines.pop(0)
    return title, "\n".join(lines).rstrip() + "\n"


def render_content(
    source: Path,
    destination: Path,
    *,
    ref: str,
    channel: str,
    available_content: set[str] | None = None,
    include_hero: bool = False,
) -> None:
    fallback = "Operating Agent Fleets" if source.name == "_index.md" else source.stem.replace("-", " ").title()
    title, body = _title_and_body(source.read_text(encoding="utf-8"), fallback)
    if source.name == "_index.md":
        title = "Operating Agent Fleets"
        if include_hero:
            body = "{{< agent-fleet-hero >}}\n\n" + body
    body = EVIDENCE_LINK.sub(
        lambda match: f"(https://github.com/pselamy/operating-agent-fleets/blob/{ref}/evidence/records/{match.group(1)})",
        body,
    )
    body = CITATION_MARKER.sub("", body)
    available = available_content or set()
    body = GUIDE_LINK.sub(
        lambda match: f"[{match.group(1)}]({match.group(2)}/)"
        if match.group(2) + ".md" in available
        else match.group(1),
        body,
    )
    frontmatter = {
        "title": title,
        "description": "A field guide to durable work, bounded authority, and systems that learn",
        "draft": channel == "preview",
        "showToc": source.name != "_index.md",
        "sourceRevision": ref,
    }
    yaml = ["---"] + [
        f'{key}: {json.dumps(value)}' for key, value in frontmatter.items()
    ] + ["---", ""]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(yaml) + body, encoding="utf-8")


def stage_bundle(site_root: Path, bundle: Path, metadata: dict[str, Any], *, ref: str, channel: str) -> None:
    targets = {name: site_root / relative for name, relative in TARGETS.items()}
    occupied = [str(path.relative_to(site_root)) for path in targets.values() if path.exists()]
    if occupied:
        raise StagingError(f"managed staging targets already exist: {', '.join(occupied)}")

    content_source = bundle / "content"
    editorial_source = bundle / "data" / "editorial-assets"
    hero_manifest = (editorial_source / "manifest.json").is_file()
    hero_image = (bundle / "static" / "agent-fleets" / "editorial" / "field-guide-hero.png").is_file()
    if hero_manifest != hero_image:
        raise StagingError("editorial hero manifest and image must be exported together")
    include_hero = hero_manifest and hero_image
    if content_source.exists():
        content_files = sorted(content_source.rglob("*.md"))
        available_content = {str(source.relative_to(content_source)) for source in content_files}
        for source in content_files:
            relative = source.relative_to(content_source)
            render_content(
                source,
                targets["content"] / relative,
                ref=ref,
                channel=channel,
                available_content=available_content,
                include_hero=include_hero,
            )

    evidence_source = bundle / "data" / "evidence"
    if evidence_source.exists():
        shutil.copytree(evidence_source, targets["data"] / "evidence")
    if editorial_source.exists():
        shutil.copytree(editorial_source, targets["data"] / "editorial-assets")
    targets["data"].mkdir(parents=True, exist_ok=True)
    (targets["data"] / "export-metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    static_source = bundle / "static" / "agent-fleets"
    if static_source.exists():
        shutil.copytree(static_source, targets["static"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=SITE_ROOT)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--channel", choices=("preview", "release"), default="preview")
    args = parser.parse_args()
    site_root = args.site_root.resolve()
    try:
        config = load_config(args.config.resolve())
        with tempfile.TemporaryDirectory(prefix="operating-agent-fleets-") as directory:
            temporary = Path(directory)
            source = checkout_source(config, temporary / "source")
            bundle = temporary / "bundle"
            metadata = run_export(source, bundle, args.channel, config)
            stage_bundle(site_root, bundle, metadata, ref=config["ref"], channel=args.channel)
    except (OSError, StagingError) as exc:
        print(f"field-guide staging failed: {exc}", file=sys.stderr)
        return 1
    print(f"staged Operating Agent Fleets {args.channel} from {config['ref']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
