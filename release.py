import os
import subprocess

subprocess.run(["python", "build.py", "--release", "--clean-cache"])
subprocess.run(
    [
        "ftcli",
        "converter",
        "ft2wf",
        "-out",
        "./website/public/fonts/",
        "-f",
        "woff2",
        "./fonts/variable/",
    ]
)
