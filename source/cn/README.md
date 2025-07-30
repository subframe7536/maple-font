## CN Font

### Directory Structure

```sh
cn
├── MapleMono-CN-Italic-VF.ttf                      # CN variable font subset
├── MapleMono-CN-Italic-VF.vfc                      # FontLab source file
├── MapleMono-CN-VF.ttf                             # CN variable font subset
├── MapleMono-CN-VF.vfc                             # FontLab source file
├── README.md
├── static                                          # Generated static CN base fonts
│   ├── MapleMonoCN-Bold.ttf
│   └── ...
└── static.sha256                                   # Hash of static fonts
```

### Development

- Download [vfc.zip](https://github.com/subframe7536/maple-font/releases/download/cn-base/vfc.zip) and then extract them into `<project-root>/source/cn`.
- Develop and generate using FontLab.
- Run `uv run task.py cn-rebuild` to generate static fonts and archives.