@echo off

set python_forge_exe="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe"

@REM available: ttf / ttf-autohint / nf
@REM 构建的基准字体
set base_font="nf"

@REM available: 0 / 1
@REM 是否修复编码和元数据，出现乱码时可尝试切换
set fix_encoding_and_meta=1

%python_forge_exe% ./SC/merge.py %base_font% %1

if %ERRORLEVEL% equ 0 (
    python ./SC/fix.py %base_font% %fix_encoding_and_meta% %1
)