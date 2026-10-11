# Installation

Download the font archives from [Releases](https://github.com/subframe7536/maple-font/releases/latest), extract the files you need, and install them with your operating system's font manager. See [Naming and Choosing Fonts](./choose.md) to decide which archive to download.

> [!NOTE]
> Maple Mono V8 is still in development, so package manager versions may not be up to date: they currently ship the v7.9 packages. If you want the latest V8 build, download it from [Releases](https://github.com/subframe7536/maple-font/releases) or [build it yourself](./build.md). For the v7.9 release, see [Releases v7.9](https://github.com/subframe7536/maple-font/releases/tag/v7.9) and the [`v7` branch](https://github.com/subframe7536/maple-font/tree/v7).

The package names below are those published for v7.9.

## Package Managers

### Scoop (Windows)

```sh
# Add bucket
scoop bucket add nerd-fonts
# Maple Mono (ttf format)
scoop install Maple-Mono
# Maple Mono NF
scoop install Maple-Mono-NF
# Maple Mono NF CN
scoop install Maple-Mono-NF-CN
```

<details>
  <summary>All packages (Click to expand)</summary>

  ```sh
  # Add bucket
  scoop bucket add nerd-fonts
  # Maple Mono (ttf format)
  scoop install Maple-Mono
  # Maple Mono (hinted ttf format)
  scoop install Maple-Mono-autohint
  # Maple Mono (otf format)
  scoop install Maple-Mono-otf
  # Maple Mono NF
  scoop install Maple-Mono-NF
  # Maple Mono NF CN
  scoop install Maple-Mono-NF-CN
  ```

</details>

### Homebrew (macOS, Linux)

```sh
# Maple Mono
brew install --cask font-maple-mono
# Maple Mono NF
brew install --cask font-maple-mono-nf
# Maple Mono NF CN
brew install --cask font-maple-mono-nf-cn
```

<details>
  <summary>All packages (Click to expand)</summary>

  ```sh
  # Maple Mono
  brew install --cask font-maple-mono
  # Maple Mono NF
  brew install --cask font-maple-mono-nf
  # Maple Mono CN
  brew install --cask font-maple-mono-cn
  # Maple Mono NF CN
  brew install --cask font-maple-mono-nf-cn

  # Maple Mono Normal
  brew install --cask font-maple-mono-normal
  # Maple Mono Normal NF
  brew install --cask font-maple-mono-normal-nf
  # Maple Mono Normal CN
  brew install --cask font-maple-mono-normal-cn
  # Maple Mono Normal NF CN
  brew install --cask font-maple-mono-normal-nf-cn
  ```

</details>

### Arch Linux

ArchLinuxCN repository allows downloading a single package zip file without downloading all the package zip files in pkgbase, but AUR does not. (If you have a good solution, please contact Cyberczy(czysheep@gmail.com))

#### ArchLinuxCN (Recommended)

```sh
# Maple Mono (Ligature TTF unhinted)
paru -S ttf-maplemono
# Maple Mono NF (Ligature unhinted)
paru -S ttf-maplemono-nf-unhinted
# Maple Mono NF CN (Ligature unhinted)
paru -S ttf-maplemono-nf-cn-unhinted
```

<details>
  <summary>All packages (Click to expand)</summary>

  ```sh
  # Maple Mono (Ligature Variable)
  paru -S ttf-maplemono-variable
  # Maple Mono (Ligature TTF hinted)
  paru -S ttf-maplemono-autohint
  # Maple Mono (Ligature TTF unhinted)
  paru -S ttf-maplemono
  # Maple Mono (Ligature OTF)
  paru -S otf-maplemono
  # Maple Mono (Ligature WOFF2)
  paru -S woff2-maplemono
  # Maple Mono NF (Ligature hinted)
  paru -S ttf-maplemono-nf
  # Maple Mono NF (Ligature unhinted)
  paru -S ttf-maplemono-nf-unhinted
  # Maple Mono CN (Ligature hinted)
  paru -S ttf-maplemono-cn
  # Maple Mono CN (Ligature unhinted)
  paru -S ttf-maplemono-cn-unhinted
  # Maple Mono NF CN (Ligature hinted)
  paru -S ttf-maplemono-nf-cn
  # Maple Mono NF CN (Ligature unhinted)
  paru -S ttf-maplemono-nf-cn-unhinted

  # Maple Mono (No-Ligature Variable)
  paru -S ttf-maplemononl-variable
  # Maple Mono (No-Ligature TTF hinted)
  paru -S ttf-maplemononl-autohint
  # Maple Mono (No-Ligature TTF unhinted)
  paru -S ttf-maplemononl
  # Maple Mono (No-Ligature OTF)
  paru -S otf-maplemononl
  # Maple Mono (No-Ligature WOFF2)
  paru -S woff2-maplemononl
  # Maple Mono NF (No-Ligature hinted)
  paru -S ttf-maplemononl-nf
  # Maple Mono NF (No-Ligature unhinted)
  paru -S ttf-maplemononl-nf-unhinted
  # Maple Mono CN (No-Ligature hinted)
  paru -S ttf-maplemononl-cn
  # Maple Mono CN (No-Ligature unhinted)
  paru -S ttf-maplemononl-cn-unhinted
  # Maple Mono NF CN (No-Ligature hinted)
  paru -S ttf-maplemononl-nf-cn
  # Maple Mono NF CN (No-Ligature unhinted)
  paru -S ttf-maplemononl-nf-cn-unhinted

  # Maple Mono Normal (Ligature Variable)
  paru -S ttf-maplemononormal-variable
  # Maple Mono Normal (Ligature TTF hinted)
  paru -S ttf-maplemononormal-autohint
  # Maple Mono Normal (Ligature TTF unhinted)
  paru -S ttf-maplemononormal
  # Maple Mono Normal (Ligature OTF)
  paru -S otf-maplemononormal
  # Maple Mono Normal (Ligature WOFF2)
  paru -S woff2-maplemononormal
  # Maple Mono Normal NF (Ligature hinted)
  paru -S ttf-maplemononormal-nf
  # Maple Mono Normal NF (Ligature unhinted)
  paru -S ttf-maplemononormal-nf-unhinted
  # Maple Mono Normal CN (Ligature hinted)
  paru -S ttf-maplemononormal-cn
  # Maple Mono Normal CN (Ligature unhinted)
  paru -S ttf-maplemononormal-cn-unhinted
  # Maple Mono Normal NF CN (Ligature hinted)
  paru -S ttf-maplemononormal-nf-cn
  # Maple Mono Normal NF CN (Ligature unhinted)
  paru -S ttf-maplemononormal-nf-cn-unhinted

  # Maple Mono Normal (No-Ligature Variable)
  paru -S ttf-maplemononormalnl-variable
  # Maple Mono Normal (No-Ligature TTF hinted)
  paru -S ttf-maplemononormalnl-autohint
  # Maple Mono Normal (No-Ligature TTF unhinted)
  paru -S ttf-maplemononormalnl
  # Maple Mono Normal (No-Ligature OTF)
  paru -S otf-maplemononormalnl
  # Maple Mono Normal (No-Ligature WOFF2)
  paru -S woff2-maplemononormalnl
  # Maple Mono Normal NF (No-Ligature hinted)
  paru -S ttf-maplemononormalnl-nf
  # Maple Mono Normal NF (No-Ligature unhinted)
  paru -S ttf-maplemononormalnl-nf-unhinted
  # Maple Mono Normal CN (No-Ligature hinted)
  paru -S ttf-maplemononormalnl-cn
  # Maple Mono Normal CN (No-Ligature unhinted)
  paru -S ttf-maplemononormalnl-cn-unhinted
  # Maple Mono Normal NF CN (No-Ligature hinted)
  paru -S ttf-maplemononormalnl-nf-cn
  # Maple Mono Normal NF CN (No-Ligature unhinted)
  paru -S ttf-maplemononormalnl-nf-cn-unhinted
  ```

</details>

#### AUR (Not Recommended)

```sh
# Maple Mono (Ligature TTF unhinted)
paru -S maplemono-ttf
# Maple Mono NF (Ligature unhinted)
paru -S maplemono-nf-unhinted
# Maple Mono NF CN (Ligature unhinted)
paru -S maplemono-nf-cn-unhinted
```

<details>
  <summary>All packages (Click to expand)</summary>

  ```sh
  # Maple Mono (Ligature Variable)
  paru -S maplemono-variable
  # Maple Mono (Ligature TTF hinted)
  paru -S maplemono-ttf-autohint
  # Maple Mono (Ligature TTF unhinted)
  paru -S maplemono-ttf
  # Maple Mono (Ligature OTF)
  paru -S maplemono-otf
  # Maple Mono (Ligature WOFF2)
  paru -S maplemono-woff2
  # Maple Mono NF (Ligature hinted)
  paru -S maplemono-nf
  # Maple Mono NF (Ligature unhinted)
  paru -S maplemono-nf-unhinted
  # Maple Mono CN (Ligature hinted)
  paru -S maplemono-cn
  # Maple Mono CN (Ligature unhinted)
  paru -S maplemono-cn-unhinted
  # Maple Mono NF CN (Ligature hinted)
  paru -S maplemono-nf-cn
  # Maple Mono NF CN (Ligature unhinted)
  paru -S maplemono-nf-cn-unhinted

  # Maple Mono (No-Ligature Variable)
  paru -S maplemononl-variable
  # Maple Mono (No-Ligature TTF hinted)
  paru -S maplemononl-ttf-autohint
  # Maple Mono (No-Ligature TTF unhinted)
  paru -S maplemononl-ttf
  # Maple Mono (No-Ligature OTF)
  paru -S maplemononl-otf
  # Maple Mono (No-Ligature WOFF2)
  paru -S maplemononl-woff2
  # Maple Mono NF (No-Ligature hinted)
  paru -S maplemononl-nf
  # Maple Mono NF (No-Ligature unhinted)
  paru -S maplemononl-nf-unhinted
  # Maple Mono CN (No-Ligature hinted)
  paru -S maplemononl-cn
  # Maple Mono CN (No-Ligature unhinted)
  paru -S maplemononl-cn-unhinted
  # Maple Mono NF CN (No-Ligature hinted)
  paru -S maplemononl-nf-cn
  # Maple Mono NF CN (No-Ligature unhinted)
  paru -S maplemononl-nf-cn-unhinted

  # Maple Mono Normal (Ligature Variable)
  paru -S maplemononormal-variable
  # Maple Mono Normal (Ligature TTF hinted)
  paru -S maplemononormal-ttf-autohint
  # Maple Mono Normal (Ligature TTF unhinted)
  paru -S maplemononormal-ttf
  # Maple Mono Normal (Ligature OTF)
  paru -S maplemononormal-otf
  # Maple Mono Normal (Ligature WOFF2)
  paru -S maplemononormal-woff2
  # Maple Mono Normal NF (Ligature hinted)
  paru -S maplemononormal-nf
  # Maple Mono Normal NF (Ligature unhinted)
  paru -S maplemononormal-nf-unhinted
  # Maple Mono Normal CN (Ligature hinted)
  paru -S maplemononormal-cn
  # Maple Mono Normal CN (Ligature unhinted)
  paru -S maplemononormal-cn-unhinted
  # Maple Mono Normal NF CN (Ligature hinted)
  paru -S maplemononormal-nf-cn
  # Maple Mono Normal NF CN (Ligature unhinted)
  paru -S maplemononormal-nf-cn-unhinted

  # Maple Mono Normal (No-Ligature Variable)
  paru -S maplemononormalnl-variable
  # Maple Mono Normal (No-Ligature TTF hinted)
  paru -S maplemononormalnl-ttf-autohint
  # Maple Mono Normal (No-Ligature TTF unhinted)
  paru -S maplemononormalnl-ttf
  # Maple Mono Normal (No-Ligature OTF)
  paru -S maplemononormalnl-otf
  # Maple Mono Normal (No-Ligature WOFF2)
  paru -S maplemononormalnl-woff2
  # Maple Mono Normal NF (No-Ligature hinted)
  paru -S maplemononormalnl-nf
  # Maple Mono Normal NF (No-Ligature unhinted)
  paru -S maplemononormalnl-nf-unhinted
  # Maple Mono Normal CN (No-Ligature hinted)
  paru -S maplemononormalnl-cn
  # Maple Mono Normal CN (No-Ligature unhinted)
  paru -S maplemononormalnl-cn-unhinted
  # Maple Mono Normal NF CN (No-Ligature hinted)
  paru -S maplemononormalnl-nf-cn
  # Maple Mono Normal NF CN (No-Ligature unhinted)
  paru -S maplemononormalnl-nf-cn-unhinted
  ```

</details>

### Nixpkgs (NixOS, Linux, macOS)

```nix
fonts.packages = with pkgs; [
  # Maple Mono (Ligature TTF unhinted)
  maple-mono.truetype
  # Maple Mono NF (Ligature unhinted)
  maple-mono.NF-unhinted
  # Maple Mono NF CN (Ligature unhinted)
  maple-mono.NF-CN-unhinted
];
```

<details>
  <summary>All packages (Click to expand)</summary>

  ```nix
  fonts.packages = with pkgs; [
    # Maple Mono (Ligature Variable)
    maple-mono.variable
    # Maple Mono (Ligature TTF hinted)
    maple-mono.truetype-autohint
    # Maple Mono (Ligature TTF unhinted)
    maple-mono.truetype
    # Maple Mono (Ligature OTF)
    maple-mono.opentype
    # Maple Mono (Ligature WOFF2)
    maple-mono.woff2
    # Maple Mono NF (Ligature hinted)
    maple-mono.NF
    # Maple Mono NF (Ligature unhinted)
    maple-mono.NF-unhinted
    # Maple Mono CN (Ligature hinted)
    maple-mono.CN
    # Maple Mono CN (Ligature unhinted)
    maple-mono.CN-unhinted
    # Maple Mono NF CN (Ligature hinted)
    maple-mono.NF-CN
    # Maple Mono NF CN (Ligature unhinted)
    maple-mono.NF-CN-unhinted

    # Maple Mono (No-Ligature Variable)
    maple-mono.NL-Variable
    # Maple Mono (No-Ligature TTF hinted)
    maple-mono.NL-TTF-AutoHint
    # Maple Mono (No-Ligature TTF unhinted)
    maple-mono.NL-TTF
    # Maple Mono (No-Ligature OTF)
    maple-mono.NL-OTF
    # Maple Mono (No-Ligature WOFF2)
    maple-mono.NL-Woff2
    # Maple Mono NF (No-Ligature hinted)
    maple-mono.NL-NF
    # Maple Mono NF (No-Ligature unhinted)
    maple-mono.NL-NF-unhinted
    # Maple Mono CN (No-Ligature hinted)
    maple-mono.NL-CN
    # Maple Mono CN (No-Ligature unhinted)
    maple-mono.NL-CN-unhinted
    # Maple Mono NF CN (No-Ligature hinted)
    maple-mono.NL-NF-CN
    # Maple Mono NF CN (No-Ligature unhinted)
    maple-mono.NL-NF-CN-unhinted

    # Maple Mono Normal (Ligature Variable)
    maple-mono.Normal-Variable
    # Maple Mono Normal (Ligature TTF hinted)
    maple-mono.Normal-TTF-AutoHint
    # Maple Mono Normal (Ligature TTF unhinted)
    maple-mono.Normal-TTF
    # Maple Mono Normal (Ligature OTF)
    maple-mono.Normal-OTF
    # Maple Mono Normal (Ligature WOFF2)
    maple-mono.Normal-Woff2
    # Maple Mono Normal NF (Ligature hinted)
    maple-mono.Normal-NF
    # Maple Mono Normal NF (Ligature unhinted)
    maple-mono.Normal-NF-unhinted
    # Maple Mono Normal CN (Ligature hinted)
    maple-mono.Normal-CN
    # Maple Mono Normal CN (Ligature unhinted)
    maple-mono.Normal-CN-unhinted
    # Maple Mono Normal NF CN (Ligature hinted)
    maple-mono.Normal-NF-CN
    # Maple Mono Normal NF CN (Ligature unhinted)
    maple-mono.Normal-NF-CN-unhinted

    # Maple Mono Normal (No-Ligature Variable)
    maple-mono.NormalNL-Variable
    # Maple Mono Normal (No-Ligature TTF hinted)
    maple-mono.NormalNL-TTF-AutoHint
    # Maple Mono Normal (No-Ligature TTF unhinted)
    maple-mono.NormalNL-TTF
    # Maple Mono Normal (No-Ligature OTF)
    maple-mono.NormalNL-OTF
    # Maple Mono Normal (No-Ligature WOFF2)
    maple-mono.NormalNL-Woff2
    # Maple Mono Normal NF (No-Ligature hinted)
    maple-mono.NormalNL-NF
    # Maple Mono Normal NF (No-Ligature unhinted)
    maple-mono.NormalNL-NF-unhinted
    # Maple Mono Normal CN (No-Ligature hinted)
    maple-mono.NormalNL-CN
    # Maple Mono Normal CN (No-Ligature unhinted)
    maple-mono.NormalNL-CN-unhinted
    # Maple Mono Normal NF CN (No-Ligature hinted)
    maple-mono.NormalNL-NF-CN
    # Maple Mono Normal NF CN (No-Ligature unhinted)
    maple-mono.NormalNL-NF-CN-unhinted
  ];
  ```

</details>


## CDN

### Maple Mono

- [fontsource](https://fontsource.org/fonts/maple-mono)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)

### Maple Mono CN

- [The Chinese Web Fonts Plan (中文网字计划)](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)
