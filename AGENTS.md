# AGENTS.md

## Purpose

Maple Mono is an open-source monospace font project. Keep changes small, deterministic, and scoped to the requested build, feature, CJK, or landing-page behavior.

## Working Rules

- Write code, comments, documentation, and commit messages in English. Reply to the repository owner in Chinese unless asked otherwise.
- Preserve unrelated user changes. Run `git status --short` before broad edits and inspect the final diff before finishing.
- Use `variable` as the default branch when reviewing branch differences.
- Do not add dependencies or change package managers without a clear need. Use `uv` for Python.
- Do not manually edit font binaries, UFO sources, or generated outputs when the repository provides a generator.
- Treat designspace and UFO sources as coupled inputs: every designspace change is accompanied by changes to the corresponding UFO sources.
- Avoid changing font names, versioning, release packaging, or output layout unless the request explicitly requires it.
- When adding or changing a `build.py` CLI flag, update the complete translated `build.py --help` section in every root README (`README.md`, `README_CN.md`, `README_TC.md`, `README_JP.md`, and `README_KR.md`) in the same change.

## Repository Map

- `build.py`: Public font-build CLI.
- `task.py`: Public task-runner CLI.
- `scripts/`: Python implementation package. Use `scripts.*` imports for cross-module imports.
  - `scripts/config/`: Build configuration, CLI parsing, and output paths.
  - `scripts/pipeline/`: Public build entrypoint, `BuildPlan`, stage orchestration,
    and output/cache lifecycle.
  - `scripts/config/resolver.py`: Build configuration and runtime resolution.
  - `scripts/cjk/cache.py`: CJK variable cache identity and manifest validation.
  - `scripts/utils/`: Filesystem, process, archive, download, errors, and version helpers.
  - `scripts/font_ops/`: Shared font and glyph operations, transforms, and protocols.
  - `scripts/cjk/`: CJK models, configuration, outline conversion,
    variable-font operations, presets, and builder.
  - `scripts/feature/`: Typed feature catalog, compiler, freeze logic, and feature application.
  - `scripts/task/`: Task-runner commands.
  - `scripts/tests/`: Python unit tests.
- `scripts/pipeline/README.md`: Orchestrator data flow, stage dependencies, cache transitions, and executor lifecycle.
- `scripts/README.md`: Global build-system architecture and ownership map.
- `scripts/maintenance.md`: Maintainer workflow for source updates, CJK bases, validation, and releases.
- `scripts/cjk/README.md`: CJK source, configuration, generation, and cache guide.
- `scripts/feature/README.md`: OpenType feature AST and generation guide.
- `sources/`: Font sources, CJK assets, schema, and generated `.fea` output in `sources/features/`.
- `config.json`: Default build configuration, validated by `sources/schema.json`.
- `fonts/`: Generated build artifacts; never edit manually.

## Setup and Commands

Use the smallest command that validates the change.

```sh
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pyrefly check
uv run python -m unittest discover -s scripts/tests
```

Useful build commands:

```sh
uv run build.py --dry
uv run build.py --ttf-only --debug
uv run build.py --ttf-only --cn --debug
uv run task.py fea
```

The downloaded `FontPatcher/` tool are intentionally excluded from root Python Ruff and Pyrefly checks.

## Validation by Change Type

- **Python changes:** Run Ruff format check, Ruff lint, Pyrefly, and the unit suite. Apply formatting with `uv run ruff format <paths>` when needed; do not hand-format generated files.
- **FontTools type-adaptation changes:** Run `uv run pyrefly check`; keep table-field types in `scripts/font_ops/fonttools.py` precise enough to expose invalid field names and values.
- **Feature changes under `scripts/feature/`:** Run `uv run task.py fea`, then inspect all generated changes before keeping them.
- **Build configuration or pipeline changes:** Start with `uv run build.py --dry`. Use `--debug`, `--ttf-only`, and `--least-styles` before attempting a full build.
- **CJK changes:** Avoid full CJK builds unless required; they may download large source archives and take a long time.

## Safe Auto-fix Workflow

After a validation command reports fixable Python issues, use this order:

```sh
uv run ruff check . --fix
uv run ruff format .
uv run ruff format --check .
uv run ruff check .
uv run pyrefly check
```

Ruff auto-fixes are limited to its default safe fixes. Pyrefly reports type diagnostics; do not apply automated type fixes or add diagnostic suppressions without reviewing the resulting diff and running the relevant unit tests or build validation.

## Generated Outputs

`uv run task.py fea` can update `sources/features/`, `sources/schema.json`, `config.json`, the localized READMEs, and `scripts/in_browser.py`. Keep these outputs synchronized when the feature source changes.

Treat `fonts/` as disposable build output. Do not commit generated churn unless it is necessary for the requested source change.

## Code Conventions

- Keep APIs focused and names explicit. Reuse nearby helpers such as `scripts/utils.py` instead of adding one-off wrappers.
- Keep import paths rooted at `scripts.*`; do not reintroduce the previous package namespace or filesystem paths.
- Keep output ordering stable to minimize generated diffs.
- Use structured parsing for JSON and font data. Add comments only for non-obvious font or build behavior.
- Pyrefly checks FontTools table fields through `scripts/font_ops/fonttools.py`. Add only verified fields and use narrow `Protocol` casts at the table boundary instead of suppressing diagnostics or casting to `Any`.

## Dependencies, Network, and Release Safety

- Python runtime dependencies belong in `pyproject.toml` and `requirements.txt`; Python development tools belong in the uv development dependency group.
- CN source downloads, Nerd Font assets, FontForge tooling, and release actions may require network access. Do not trigger them unless the task needs them.
- Never run release, publish, push, or destructive cleanup commands unless explicitly requested.

## Before Finishing

- Verify the changed files with `git diff --check`, `git diff --stat`, or `git status --short`.
- Run the smallest relevant validation commands and report anything skipped.
- Call out generated files and submodule changes explicitly.
