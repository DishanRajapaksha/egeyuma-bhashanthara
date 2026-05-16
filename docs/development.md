---
sidebar_position: 99
---

# Development

## Python checks

```bash
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Documentation site

The documentation site is built with Docusaurus.

```bash
npm --prefix docs-site install
npm --prefix docs-site run start
npm --prefix docs-site run build
```

## Publishing docs

The `Publish docs` GitHub Actions workflow builds Docusaurus and deploys the `build/` directory to GitHub Pages.

The workflow runs on pushes to `main` that change docs, Docusaurus config, or workflow files. It can also be run manually with `workflow_dispatch`.

GitHub Pages must be configured to use GitHub Actions as the source in the repository settings.
