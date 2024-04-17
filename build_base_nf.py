from fontTools.varLib import TTFont
from fontTools.subset import Subsetter

file = "fonts/nf/MapleMono-NF-Regular.ttf"

font = TTFont(file)
subsetter = Subsetter()
subsetter.populate(
    unicodes=range(0xE000, 0xF1AF0),
)
subsetter.subset(font)

# font.save("source/NerdFontBase.ttf")
font.save("source/NerdFontBaseMono.ttf")
font.close()
