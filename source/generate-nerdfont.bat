@echo off

set python_exe="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe"
set font_dir=..\output\ttf
set output_dir=..\output\NF
set args=-l -c --careful

if not exist %font_dir% (
    echo Font directory does not exist: %font_dir%
    exit /b 1
)

set font_name=%1

if %2==1 (
    set args=%args% -s
)

if %3==1 (
    set font_dir=%font_dir%-autohint
)

set font_path=%font_dir%\%font_name%.ttf

if not exist %font_path% (
    echo Font file does not exist: %font_path%
    exit /b 1
)

%python_exe% %cd%\FontPatcher\font-patcher %args% --outputdir %output_dir% %font_path%