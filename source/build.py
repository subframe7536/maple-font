from fontTools import ttx
import os
from os import path as path

root=os.getcwd()
source=path.join(root,"ttx")
output=path.join(root,"output")
if not path.exists(path.join(output,"otf")):
  os.makedirs(path.join(output,"otf"))
if not path.exists(path.join(output,"ttf")):
  os.makedirs(path.join(output,"ttf"))
print("=== build start ===")
for f in os.listdir(source):
  print(f)
  jobs, options = ttx.parseOptions([
    "-o",
    path.join(output,"ttf",f+".ttf"),
    path.join(source,f,f+".ttx")
  ])
  ttx.process(jobs,options)
  jobs, options = ttx.parseOptions([
    "-o",
    path.join(output,"otf",f+".otf"),
    path.join(source,f,f+".ttx")
  ])
  ttx.process(jobs,options)
print("=== build end ===")