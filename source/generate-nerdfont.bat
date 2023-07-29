@echo off

set python_exe="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe"
set output_dir=..\output\NF

set font_dir=..\output\ttf
if %3==1 (
    set font_dir=%font_dir%-autohint
)
if not exist %font_dir% (
    echo Font directory does not exist: %font_dir%
    exit /b 1
)

@REM full args: https://github.com/ryanoasis/nerd-fonts#font-patcher
set args=-l -c --careful
if %2==1 (
    set args=%args% -s
)


set font_name=%1


set target_font_path=%font_dir%\%font_name%.ttf

if not exist %target_font_path% (
    echo Font file does not exist: %target_font_path%
    exit /b 1
)

%python_exe% %cd%\FontPatcher\font-patcher %args% --outputdir %output_dir% %target_font_path%