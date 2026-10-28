# Development

This page is a quick start for contributors. The maintainer workflow (source updates, generated files, CJK base refreshes, validation, and releases) lives in [`scripts/maintenance.md`](../scripts/maintenance.md), and the build-system architecture is described in [`scripts/README.md`](../scripts/README.md). Those documents are the source of truth; this page only links to them.

## Design

The glyphs are designed in [FontLab](https://www.fontlab.com/). Edit the tracked `.vfc` source, export the matching `.glyphs` file, and regenerate the committed Designspace and UFO sources with `uv run task.py designspace`. See [Update the Maple Mono source](../scripts/maintenance.md#update-the-maple-mono-source) for the full procedure.

## Setup and Common Commands

```sh
# Init project
uv sync
# Inspect the resolved build configuration
uv run build.py --dry
# Fast debug build (TTF only)
uv run build.py --format ttf --debug
# Fast debug build with Simplified Chinese
uv run build.py --format ttf --cjk cn --debug
# Update fea files, feature documentation, schema, and config
uv run task.py fea
# Update Nerd Font base fonts
uv run task.py nf
# Regenerate Designspace and UFO sources from Glyphs exports
uv run task.py designspace
# Build preset CJK base fonts
uv run task.py cjk --preset cn
# Build Google Fonts assets
uv run task.py googlefonts
# Release (preview first with --dry)
uv run task.py release --dry
```

All `task.py` commands: `nf`, `fea`, `designspace`, `release`, `cjk`, `googlefonts`, `publish`. Run `uv run task.py <name> --help` for their options.

> [!WARNING]
> `uv run task.py release` commits and pushes a version tag. Follow [Create a Maple Mono release](../scripts/maintenance.md#create-a-maple-mono-release) before running it.

## Validation

See the [validation baseline](../scripts/maintenance.md#validation-baseline):

```sh
uv run ruff format --check .
uv run ruff check .
uv run pyrefly check
uv run python -m unittest discover -s scripts/tests
```

## Related Guides

- [`build.py` CLI reference](./cli.md)
- [Google Fonts build and QA](./google-fonts.md)
- [CJK source, configuration, generation, and cache guide](../scripts/cjk/README.md)
- [OpenType feature generation guide](../scripts/feature/README.md)
- [Pipeline data flow](../scripts/pipeline/README.md)
