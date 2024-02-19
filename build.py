from fontTools.varLib import TTFont, mutator
from os import mkdir, path
import shutil

input_dir = "src-font"
output_dir = "fonts"

input_files = ["MapleMono[wght]-VF.ttf", "MapleMono-italic[wght]-VF.ttf"]


if path.exists(output_dir):
    shutil.rmtree(output_dir)

mkdir(output_dir)
mkdir(path.join(output_dir, "variable"))
mkdir(path.join(output_dir, "ttf"))
mkdir(path.join(output_dir, "otf"))
# mkdir(path.join(output_dir, "woff2"))

# fixes varaible fonts
# for input_file in input_files:
#     font = TTFont(path.join(input_dir, input_file))

#     font["post"].__dict__["isFixedPitch"] = 1
#     font["OS/2"].xAvgCharWidth = 600

#     font.save(path.join(input_dir, input_file))

# instantiate fonts
instance_weight = {
    "Thin": 100,
    "ExtraLight": 220,
    "Light": 310,
    "Regular": 400,
    "Medium": 460,
    "SemiBold": 520,
    "Bold": 680,
    "ExtraBold": 800,
}
for input_file in input_files:
    font = TTFont(path.join(input_dir, input_file))
    for styleName, weight in instance_weight.items():
        newFont = mutator.instantiateVariableFont(font, {"wght": weight})
        newFont.saveXML(path.join(output_dir, "ttf", f"{weight}-{styleName}.ttx"))
