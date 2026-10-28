# Custom Build

Maple Mono can be rebuilt from source with your own options. The [`config.json`](../config.json) file configures the build process; check the [schema](../sources/schema.json) and the [OpenType feature documentation](./opentype-features.md) for the complete configuration surface.

Command-line options have a higher priority than options in `config.json`. See:

- [Build Options](./build-options.md) for what each option does (width, Nerd Font, Normal preset, feature freezing, line height, weight mapping, and more).
- [CJK Build](./cjk.md) for Simplified Chinese, Traditional Chinese, Japanese, and Korean builds.
- [`build.py` CLI reference](./cli.md) for the full list of command-line flags, or run `python build.py --help` after installing dependencies.

## Build Methods

### 1. Build In Browser

Go to [Playground](https://font.subf.dev/en/playground), and click the "Custom Build" button in the bottom left corner

- Only supports freezing OpenType features currently.

### 2. Use GitHub Actions

You can use [Github Actions](https://github.com/subframe7536/maple-font/actions/workflows/custom.yml) to build the font.

1. Fork the repo.
2. (Optional) Change the content in `config.json`.
3. Go to the Actions tab.
4. Click on the `Custom Build` menu item on the left.
5. Click on the `Run workflow` button with options set.
6. Wait for the build to finish.
7. Download the font archives from Releases.

### 3. Use Docker

```shell
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable
cd maple-font
docker build -t maple-font .
docker run -v "$(pwd)/fonts:/app/fonts" -e BUILD_ARGS="--normal" maple-font
```

### 4. Local Build

V8 is currently available from the `variable` branch. Make sure you have Python 3.10+ and `pip` installed.

```shell
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable
cd maple-font
pip install -r requirements.txt
python build.py
```

If you use [uv](https://docs.astral.sh/uv/), run `uv sync` and then `uv run build.py` instead.

> [!TIP]
> For `Ubuntu` or `Debian`, maybe `python-is-python3` is needed as well.
>
> If you have trouble installing the dependencies, just create a new GitHub Codespace and run the commands there.

The commands above build the development version and write generated fonts under `fonts/`. They do not replace the v7.9 packages already installed by Scoop, Homebrew, Arch, Nix, or a CDN.

## GitHub Mirror

The build script automatically downloads required resources from GitHub. If a download fails, set `github_mirror` in [config.json](../config.json) or set `$GITHUB` as an environment variable. The target URL format is `https://<github_mirror>/<user>/<repo>/releases/download/<tag>/<file>`; you can also download the target `.zip` file and place it next to `build.py`.
