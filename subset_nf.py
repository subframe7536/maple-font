from fontTools.varLib import TTFont
from fontTools.subset import Subsetter
import os

os.makedirs("subset", exist_ok=True)

file = "fonts/nf/MapleMono-NF-Regular.ttf"

font = TTFont(file)
subsetter = Subsetter()
subsetter.populate(
    unicodes=range(0xE000, 0xF1AF0),
)
subsetter.subset(font)

font.save("src-fonts/NerdFontBase.ttf")
font.close()
