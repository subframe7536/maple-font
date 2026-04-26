## KO Font

### Directory Structure

```sh
ko
├── NotoSansMonoCJKkr-VF.ttf             # Korean Mono variable source from Noto CJK
├── NotoSansMonoCJKkr-Regular.otf        # Korean Mono static fallback source
├── NotoSansMonoCJKkr-Bold.otf           # Korean Mono static fallback source
├── README.md
├── static                              # Generated static KO base fonts
│   ├── MapleMonoKO-Bold.ttf
│   └── ...
└── static.sha256                       # Hash of generated static fonts
```

### Development

- Run `uv run task.py ko --pull` to download Korean-only Noto CJK source fonts.
- Run `uv run task.py ko --rebuild` to generate static KO base fonts.
- The KO source must remain Noto Sans Mono CJK KR only. Do not use JP, SC, TC, or HK Noto CJK fonts.
