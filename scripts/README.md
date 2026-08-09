# Maple Mono Build System

This directory implements `build.py` and `task.py`. The build pipeline is deterministic only when its source inputs, generated feature files, and resolved configuration are kept in sync, so use the ownership map below before changing an input or a stage. For source updates, CJK base maintenance, validation, and releases, follow [`maintenance.md`](maintenance.md).

## Start here

| Need                       | Entry point                                | What it does                                                                                                                   |
| -------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Inspect the resolved build | `uv run build.py --dry`                    | Resolves configuration and prints the local config plus runtime context, without constructing a `BuildPlan` or building fonts. |
| Build release outputs      | `uv run build.py`                          | Runs the complete pipeline selected by the resolved configuration.                                                             |
| Build a focused format     | `uv run build.py --format ttf --debug`     | Selects a requested base format and the debug style/output policy.                                                             |
| Build CJK base assets      | `uv run task.py cjk --preset cn`           | Rebuilds the standalone CJK variable bases and variable archive/hash, then static bases unless `--vf-only` is set.              |
| Run a repository task      | `uv run task.py <name>`                    | Dispatches feature, designspace, Nerd Font, page, release, and publish workflows.                                              |
| Follow maintenance steps   | [`maintenance.md`](maintenance.md)         | Covers source updates, generated files, CJK base refreshes, validation, and release procedures.                                |
| Trace pipeline state       | [`pipeline/README.md`](pipeline/README.md) | Documents stage selection, cache transitions, failure state, and executor ownership.                                           |

`build.py` owns final outputs under `fonts/`. `task.py cjk` owns reusable CJK inputs under `source/cjk/`; its cache is independent of
`fonts/build-cache.json`.

## Ownership map

| Area                   | Source of truth                                         | Responsibility                                                                                                           |
| ---------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Configuration          | `config/base.py`, `config/resolver.py`, `config/cli.py` | Parse JSON and CLI values, normalize defaults, validate selections, and derive the resolved build model.                 |
| Runtime decisions      | `config/runtime.py`, `config/paths.py`                  | Resolve output paths, CJK base fallback, downloads, and runtime flags.                                                   |
| Build orchestration    | [`pipeline/orchestrator.py`](pipeline/orchestrator.py)  | Select stages, coordinate dependencies, manage cache state, and archive outputs.                                         |
| Fontmake base build    | `pipeline/fontmake.py`                                  | Prepare Designspace/UFO sources, compile Fontmake branches, and post-process base Variable/TTF/OTF fonts.                |
| Derived base outputs   | `pipeline/base_fonts.py`                                | Apply AutoHint to static TTFs and convert static TTFs to WOFF2. It does not compile or post-process Fontmake base fonts. |
| Nerd Font              | `pipeline/nerd_fonts.py`, `font_ops/nerd_font.py`       | Build from prebuilt Nerd Font assets or Font Patcher, then apply Maple naming and metrics.                               |
| CJK integration        | `pipeline/cjk_outputs.py`, `cjk/`                       | Resolve CJK bases, merge them with Maple or NF fonts, and publish static or variable profiles.                           |
| Shared font operations | `font_ops/`                                             | Keep naming, metrics, glyph transforms, OpenType edits, merging, subsetting, and FontTools boundaries reusable.          |
| OpenType features      | `feature/`                                              | Generate and apply rules; checked-in `.fea` files live under `source/features/`.                                         |
| Task adapters          | `task/`                                                 | Keep repository maintenance workflows thin and separate from the release pipeline.                                       |
| Infrastructure         | `utils/`                                                | Provide filesystem, process, archive, download, logging, error, and version helpers.                                     |

## Build lifecycle

1. **Resolve inputs.** `config.json` and CLI flags become `ResolvedConfig`, and normalization happens here rather than inside stages.
2. **Handle dry-run early.** `main()` resolves `ResolvedConfig` and `BuildRuntimeContext`, then prints and exits for `--dry`; it does not create `BuildPlan`. Local stdout contains labeled `resolved_config` and `runtime_context` JSON, while CI stdout contains only the resolved config JSON so it can be parsed directly. Warnings remain on stderr.
3. **Create the plan.** A normal build constructs `BuildPlan`, which selects target styles, required base formats, WOFF2, Nerd Font, CJK profiles, cleanup, and archive policy once.
4. **Prepare and compile base fonts.** `fontmake.py` prepares the committed Designspace/UFO sources, compiles Fontmake Variable/TTF/OTF branches, and applies the base-font post-processing before publishing outputs.
5. **Build derived outputs.** `base_fonts.py` consumes static TTF outputs for AutoHint and WOFF2. Nerd Font and CJK stages consume only the outputs selected by their dependency policy.
6. **Finalize.** If TTF was not requested, the pipeline removes `fonts/TTF/` and `fonts/TTF-AutoHint/` after all consumers finish. It writes `build-config.json` before work starts and rewrites it on successful completion; it refreshes `build-cache.json` only after the complete pipeline succeeds. A failed build can therefore leave a new config beside an old or missing cache. If `--archive` is enabled, every non-JSON output directory that exists at archive time is processed; `--cache` does not limit this to NF/CJK.

## Output layout

| Output                        | Produced by                             | Reused by                                                    |
| ----------------------------- | --------------------------------------- | ------------------------------------------------------------ |
| `fonts/Variable/`             | Base Variable stage                     | Variable consumers and CJK variable merges.                  |
| `fonts/Variable-NF/`          | Default variable Nerd Font stage        | Base variable fonts with Nerd Font glyphs.                   |
| `fonts/NFMono/`, `fonts/NFPropo/` | Fixed/proportional NF stages         | Custom static NF variants; release jobs publish unhinted packages from both directories. |
| `fonts/Variable-NFMono/`, `fonts/Variable-NFPropo/` | Custom variable NF stages | Local Mono/Propo variable builds; these variants are not published. |
| `fonts/TTF/`, `fonts/OTF/`    | Base static stages                      | AutoHint, WOFF2, Nerd Font, CJK static merges, and archives. |
| `fonts/TTF-AutoHint/`         | AutoHint stage                          | Nerd Font and hinted CJK static merges.                      |
| `fonts/Woff2/`                | WOFF2 conversion stage                  | Web distribution and archives.                               |
| `fonts/NF/`                   | Nerd Font stage                         | NF-CJK static or variable merges.                            |
| `fonts/<LOCALE>/`             | Plain CJK integration stage             | Release archives and downstream consumers.                   |
| `fonts/NF-<LOCALE>/`          | Default NF-CJK integration stage        | Release archives and downstream consumers.                   |
| `fonts/NFMono-<LOCALE>/`, `fonts/NFPropo-<LOCALE>/` | Custom NF-CJK integration stages | Local Mono/Propo CJK builds; these variants are not published. |
| `fonts/Variable-<LOCALE>/`    | Plain CJK variable stage                | Release archives and downstream consumers.                   |
| `fonts/Variable-NF-<LOCALE>/` | Default NF-CJK variable stage           | Release archives and downstream consumers.                   |
| `fonts/Variable-NFMono-<LOCALE>/`, `fonts/Variable-NFPropo-<LOCALE>/` | Custom NF-CJK variable stages | Local Mono/Propo CJK variable builds; these variants are not published. |
| `fonts/build-config.json`     | Build start and successful finalization | Reproducing the resolved build inputs.                       |
| `fonts/build-cache.json`      | Successful finalization only            | Independent stage reuse on the next cached build.            |

Everything under `fonts/` is generated output. Change sources, configuration, or generators instead of editing generated files by hand.

## Cache contract

The main cache is opt-in and lives at `fonts/build-cache.json`. A cache hit requires the recorded stage identity, exact expected output paths, file existence, and file digest to match. A miss preserves existing and unrelated files; it does not clear the stage directory. For a CJK miss, the pipeline first removes only that CJK stage's cache record so other locale/profile records remain usable.

Stage identities contain only the related resolved configuration, target styles, the regular and italic Designspace dimension dictionaries, the generated feature file fingerprint, and upstream stage identities. They do not include generator source code, dependency versions, UFO outline contents, or CJK base contents. After changing any of those untracked identity inputs, run without `--cache` so the result cannot be mistaken for a valid cached build.

The CJK base cache under `source/cjk/` is separate. `build.py --cache` controls final outputs under `fonts/`; `cjk.clean_cache` controls reuse of CJK variable or source fallback work, but it does not delete files and does not bypass a valid static directory digest.
