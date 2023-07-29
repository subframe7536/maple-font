@echo off

set name=MapleMono
set dir=fonts

if not exist %dir% (
  echo Fail: font dir not exist
  exit
)

if exist .\ttx rmdir /s /q .\ttx

ttx -s -f -d .\ttx\%name%-Regular .\%dir%\%name%-Regular.ttf
ttx -s -f -d .\ttx\%name%-Bold .\%dir%\%name%-Bold.ttf
ttx -s -f -d .\ttx\%name%-Light .\%dir%\%name%-Light.ttf
ttx -s -f -d .\ttx\%name%-Italic .\%dir%\%name%-Italic.ttf
ttx -s -f -d .\ttx\%name%-BoldItalic .\%dir%\%name%-BoldItalic.ttf
ttx -s -f -d .\ttx\%name%-LightItalic .\%dir%\%name%-LightItalic.ttf