pyinstaller -y --clean ^
--distpath="." ^
--onefile ^
--name=PriconneUtils ^
--icon=.\testout.ico ^
.\scripts\Run.py

:: If you don't have a .ico file, just delete the --icon line
:: If you do have a .ico file, replace .\testout.ico with the path to your .ico file