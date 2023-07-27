@echo off

set python_exe="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe"

@REM available: ttf / ttf-autohint / nf
set base_font="nf"

python ./build.py

%python_exe% ./SC/merge.py %base_font%

python ./SC/fix.py %base_font%