import importlib.util
from os import mkdir, path
import shutil
import subprocess

package_name = "foundryToolsCLI"
package_installed = importlib.util.find_spec(package_name) is not None

if not package_installed:
    print(
        f"{package_name} is not found. Please install it using `pip install foundryToolsCLI`"
    )
    exit(1)


def run(cli: str):
    subprocess.run(cli.split(" "), shell=True)


input_files = [
    "src-font/MapleMono[wght]-VF.ttf",
    "src-font/MapleMono-Italic[wght]-VF.ttf",
]
output_dir = "fonts"
output_otf = path.join(output_dir, "otf")
output_ttf = path.join(output_dir, "ttf")
output_ttf_autohint = path.join(output_dir, "ttf-autohint")
output_variable = path.join(output_dir, "variable")
output_woff2 = "woff2"

shutil.rmtree(output_dir, ignore_errors=True)
shutil.rmtree("woff2", ignore_errors=True)
mkdir(output_dir)
mkdir(output_variable)

for input_file in input_files:
    run(f"ftcli converter vf2i {input_file} -out {output_ttf}")
    run(f"ftcli converter ttf2otf {output_ttf} -out {output_otf}")
    run(f"ftcli converter ft2wf {output_ttf} -out {output_woff2} -f woff2")
    run(f"ftcli ttf autohint {output_ttf} -out {output_ttf_autohint}")
    shutil.copy(input_file, output_variable)
