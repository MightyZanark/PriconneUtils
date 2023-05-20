pyinstaller -y --clean ^
--distpath="." ^
--onefile ^
--name=PriconneUtils ^
.\scripts\Run.py

pause
:: If you don't have a .ico file, just delete the --icon line
:: If you do have a .ico file, replace .\testout.ico with the path to your .ico file