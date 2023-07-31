## Build Steps

### 1. Clone the repo

```shell
git clone https://github.com/subframe7536/Maple-font --depth 1
cd ./Maple-font/source
```

### 2. Install required Python package

```shell
pip install -r requirements.txt
```

#### Install FontForge (optional)

to patch Nerd Font, please make sure [FontForge](https://fontforge.org/) and its Python module are installed

### 3. Modify build config (optional)

if you want to custom build the font, like freeze some font features, you can modify the config option in [build.py](./build.py)

### 4. Run Build Script

```shell
python build.py
```

if you want to patch Nerd Font version, the script will auto download Font Patcher from Github Release, or you can manully download from https://github.com/ryanoasis/nerd-fonts/releases/download/latest/FontPatcher.zip and put it to `<project root>/source` dir

### 5. Result

you can find the completed fonts and build config in `<project root>/output`

## Build with Chinese characters

see [doc](https://github.com/subframe7536/maple-font/blob/chinese/source/README_CN.md)