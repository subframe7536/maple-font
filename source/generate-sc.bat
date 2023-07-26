@echo off

set python_exe="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe"

python ./build.py

%python_exe% ./SC/merge.py

python ./SC/fix.py