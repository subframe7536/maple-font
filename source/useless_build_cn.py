# 只是个架子，没法用
import os
from os import path
import fontforge

root=os.getcwd()
output=path.join(root,"output")
cn_output=path.join(root,"cn")

print("merge CN start")
for f in os.listdir(output):
  if not f == "Maple Mono NF.ttf":
    base_path=path.join(output,f)
    add_path=path.join(cn_output,"subset "+f.replace("Mono","UI"))
    print(f)
    base_font=fontforge.open(base_path)
    add_font=fontforge.open(add_path)
    base_font.selection.select(("ranges","unicode"),"2E80","D7A3")
    add_font.selection.select(("ranges","unicode"),"2E80","D7A3")
    add_font.copy()
    base_font.paste()
    base_font.selection.select(("ranges","unicode"),"FA49","FE47")
    add_font.selection.select(("ranges","unicode"),"FA49","FE47")
    add_font.copy()
    base_font.paste()
    base_font.generate(path.join(cn_output,f.replace("Mono","Mono CN")))
    base_font.close()
    add_font.close()

print("build end")