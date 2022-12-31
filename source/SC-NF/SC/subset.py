import shutil
from fontTools import subset
import os
from os import path

cn_path=os.getcwd();
cn_output=path.join(cn_path,"subset")

print("=== subset CN start ===")

if path.exists(cn_output):
  shutil.rmtree(cn_output)
os.mkdir(cn_output)

for f in os.listdir(cn_path):
  # if ".ttf" in f:
  if not "UI" in f and "ttf" in f:
    print(f)
    subset.main([
      path.join(cn_path,f),
      "--unicodes=%s" % "3001,3002,3007-3011,3400-9fff,ff5e,ff01,ff08,ff09,ff0c,ff1a,ff1b,ff1f",
      "--glyph-names",
      # "--no-notdef-glyph",
      # "--hinting-tables='*'",
      "--output-file=%s" %  path.join(cn_output,f)
    ])
print("=== subset CN end ===")
f=open(path.join(cn_output,"italic.txt"),'w')
f.write('''Open("Maple.ttf")
SelectAll()
# Move(0,40)
# Generate("Maple.ttf")
# Print("== Maple centered Generated ==")
Italic(-12)
Generate("Maple Italic.ttf")
Print("")
Print("== Maple Italic centered Generated ==")
Print("")
Close()
Open("Maple Bold.ttf")
SelectAll()
# Move(0,40)
# Generate("Maple Bold.ttf")
# Print("== Maple Bold centered Generated ==")
Italic(-12)
Generate("Maple Bold Italic.ttf")
Print("")
Print("== Maple Bold Italic centered Generated ==")
Print("")
Close()
''')
# f.write('''Open("Maple UI.ttf")
# SelectAll()
# Move(0,40)
# Generate("Maple UI.ttf")
# Print("== Maple UI centered Generated ==")
# Italic(-12)
# Generate("Maple UI Italic.ttf")
# Print("")
# Print("== Maple UI Italic centered Generated ==")
# Print("")
# Close()
# Open("Maple UI Bold.ttf")
# SelectAll()
# Move(0,40)
# Generate("Maple UI Bold.ttf")
# Print("== Maple UI Bold centered Generated ==")
# Italic(-12)
# Generate("Maple UI Bold Italic.ttf")
# Print("")
# Print("== Maple UI Bold Italic centered Generated ==")
# Print("")
# Close()
# ''')
f.flush()
f.close()