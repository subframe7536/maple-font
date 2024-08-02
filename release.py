import subprocess

subprocess.run(["python", "build.py", "--release"])
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
