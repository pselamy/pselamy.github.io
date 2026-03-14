# selamy.dev — Personal Website

Hugo static site deployed to GitHub Pages via GitHub Actions.

## Quick Reference

- **URL**: https://selamy.dev (also: selamy.nyc redirects here)
- **Theme**: PaperMod (git submodule in `themes/PaperMod`)
- **Config**: `hugo.toml`
- **Content**: `content/posts/<post-slug>/index.md`

## Content Structure

```
content/
  posts/
    <post-slug>/
      index.md          <- post content (Hugo page bundle)
  about.md              <- about page
```

## Required Frontmatter

Every post in `content/posts/` must have:

```yaml
---
title: "Post Title"
date: 2026-03-14T12:00:00-05:00
slug: "post-slug"
description: "One-line summary for SEO and social cards."
tags: ["tag1", "tag2"]
draft: false
---
```

Optional: `series`, `showToc`, `cover`.

## CI Quality Gate

PRs that touch `content/**` trigger `.github/workflows/quality-gate.yml`:

- **Layer 1 (Structural)**: markdownlint, frontmatter validation, word count
- **Layer 2 (Content Safety)**: privacy scanner — no org names (Matchpoint, TradeStream, VeinRoute, Velix, loam-dev), no internal emails, no repo names that leak org structure
- **Layer 3 (Writing Quality)**: Vale prose linter (warnings only, non-blocking)
- **Layer 5 (Build Check)**: Hugo must build successfully

Branch protection requires Layer 1, 2, and 5 to pass before merge.

## Local Development

```bash
hugo server --buildDrafts    # Preview at localhost:1313
hugo --gc --minify           # Production build to public/
```

## Privacy Rules

Content on this site is framed as personal side projects. Do not mention:
- Employer name or internal projects
- Org names from other side projects (Matchpoint, TradeStream, etc.)
- Real usernames, internal repo names, or email addresses
- Use generic/anonymized examples when referencing multi-org work

## Deploy

Push to `main` → GitHub Actions builds Hugo → deploys to GitHub Pages. Auto-deploy, no manual steps.
