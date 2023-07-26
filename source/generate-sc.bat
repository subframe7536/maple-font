@echo off

set python_exe="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe"

%python_exe% ./SC/merge.py

python ./SC/fix.py