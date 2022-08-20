@echo off
set root=%cd%
set name=MapleMono
set tempname=Maple Mono SC NF
set finalname=MapleMono-SC-NF
set ff="C:\Program Files (x86)\FontForgeBuilds\bin\fontforge.exe" -script
set nf="C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe" %root%\nerd-fonts\font-patcher -l -s --careful -c
set scnfout=..\..\output\SC-NF


cd .\SC
cls
echo ===== add Nerd Font for Regular =====
%nf% %name%-Regular.ttf
cls
echo ===== add Nerd Font for Bold =====
%nf% %name%-Bold.ttf
cls
echo ===== add Nerd Font for Italic =====
%nf% %name%-Italic.ttf
cls
echo ===== add Nerd Font for BoldItalic =====
%nf% %name%-BoldItalic.ttf

cls
echo ===== add Nerd Font =====
echo ===== merge SC for Regular =====
%ff% merge.txt "%tempname% Regular.ttf" regular.ttf %finalname%-Regular.ttf
cls
echo ===== add Nerd Font =====
echo ===== merge SC for Bold =====
%ff% merge.txt "%tempname% Bold.ttf" Bold.ttf %finalname%-Bold.ttf
cls
echo ===== add Nerd Font =====
echo ===== merge SC for Italic =====
%ff% merge.txt "%tempname% Italic.ttf" Italic.ttf %finalname%-Italic.ttf
cls
echo ===== add Nerd Font =====
echo ===== merge SC for BoldItalic =====
%ff% merge.txt "%tempname% BoldItalic.ttf" BoldItalic.ttf %finalname%-BoldItalic.ttf

@REM cls
@REM echo ===== add Nerd Font =====
@REM echo ===== merge SC =====
@REM echo ===== fix OS/2 =====
@REM if not exist %scnfout% md %scnfout%
@REM 生成otf的OS/2 ttx，结合一下
@REM ttx -o %scnfout%\%finalname%-Regular.ttf -m %finalname%-Regular.ttf ..\os2\%name%-Regular.ttx
@REM ttx -o %scnfout%\%finalname%-Bold.ttf -m %finalname%-Bold.ttf ..\os2\%name%-Bold.ttx
@REM ttx -o %scnfout%\%finalname%-Italic.ttf -m %finalname%-Italic.ttf ..\os2\%name%-Italic.ttx
@REM ttx -o %scnfout%\%finalname%-BoldItalic.ttf -m %finalname%-BoldItalic.ttf ..\os2\%name%-BoldItalic.ttx

cls
echo ===== add Nerd Font =====
echo ===== merge SC =====
@REM echo ===== fix OS/2 =====
echo ===== clear temp =====

del Maple*
pause