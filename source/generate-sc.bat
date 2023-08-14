@echo off

set python_forge_exe="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe"

@REM available: ttf / ttf-autohint / nf
set base_font="nf"

%python_forge_exe% ./SC/merge.py %base_font% %1

if %ERRORLEVEL% equ 0 (
    python ./SC/fix.py %base_font% %1
)