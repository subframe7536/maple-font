## 构建步骤

### 1. 克隆仓库

```shell
git clone https://github.com/subframe7536/Maple-font --depth 1 -b chinese
cd ./Maple-font/source
```

### 2. 安装必要的 Python 包

```shell
pip install -r requirements.txt
```

#### 安装 FontForge (可选)

为构建 Nerd Font 版本，请确保系统中已安装 [FontForge](https://fontforge.org/) 和它的 Python 模块

### 3. 修改构建配置 (可选)

如果你想修改构建配置，例如固定某些字体特性，你可以修改 [build.py](./build.py) 中的配置

如果你只想构建 Maple Mono SC，你可以修改 `generate-sc.bat`，将 `base_font` 改为 `"ttf"` 或者 `"ttf-autohint"`

### 4. 运行构建脚本

当前只支持 Windows 构建，欢迎 **PR**

```shell
python build.py
```

如果你想构建 Nerd Font 版本，脚本会自动从 Github 上下载 Font Patcher，或者手动将 https://github.com/ryanoasis/nerd-fonts/releases/download/latest/FontPatcher.zip 下载下来，放到 `<project root>/source` 中

### 5. 结果

构建好的字体和构建配置在 `<project root>/output`