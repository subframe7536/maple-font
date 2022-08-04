from fontTools import ttx
import os
from os import path as path

root=os.getcwd()
source=path.join(root,"ttx")
output=path.join(root,"output")
if not path.exists(output):
  os.mkdir(output)
for f in os.listdir(source):
  print(f)
  jobs, options = ttx.parseOptions([
    "-o",
    path.join(output,f).replace(".ttx",".ttf"),
    path.join(source,f)
  ])
  ttx.process(jobs,options)