# Priconne Utils

Scripts written in Python to get the master database, BGM files, L2D, UB Cutin, etc. from the game Princess Connect! Re: Dive JP Server. Made and compiled in Windows 10, so it might not work as intended on other OSs.


## Requirements

- Internet Connection (obviously)
- [acb2wavs (for audio files)](https://github.com/hozuki/libcgss)
- [FFmpeg (for video and audio files)](https://ffmpeg.org/download.html)


## How to Use

1. Well first of all, install all the requirements, won't work without it.
2. If you haven't already, add acb2wavs and FFmpeg to PATH in System Variables. If you don't know how to do that then check out the later section.
3. Don't forget to download the executable from [latest](https://github.com/MightyZanark/PriconneUtils/releases/latest).
4. If you got everything set up already, then you can double click on `PriconneUtils.exe` to run the program. After running, a window will pop up and there are instructions there as well.
5. Type the option that you would like to do, upper/lowercases doesn't matter.
6. After the program runs the option you selected, it will ask you if you want to continue on to another option or to stop. Just write a simple `y` (yes) or `n` (no) as indicated.
7. And that is it. The L2D, cutin, etc will be saved in a folder created right where the `PriconneUtils.exe` file is, so if you don't want to bother moving the output files elsewhere later, make sure to place the executable where you want it.


## How to Add to PATH (Windows 10)

1. Open up the search bar and search for `system variables`, `Edit the system environment variables` should appear so click on it.
2. A window called `System Properties` should open and you should be in the `Advanced` tab.
3. At the very bottom, there should be a button called `Environment Variables...`, click that.
4. Another window called `Environment Variables` should open up. There are 2 section in it, the upper part is the variables for the **CURRENT USER**, while the bottom part is for the **WHOLE SYSTEM** (or ALL USER). You can choose whether you like acb2wavs and FFmpeg to be available to only the **CURRENT USER** or to **ALL USER**.
5. After you decided which one you want to edit, find the variable called `Path` (not `PATHEXT`), select it, and press `Edit` or double click it. That should open up yet another window.
6. In that window, there should be all kinds of options like `New`, `Edit`, `Browse`, `Delete`, etc. To add acb2wavs and UsmToolkit to it, press `New`.
7. Copy and paste the full path of acb2wavs and UsmToolkit, and by full path I meant something like this `D:\libcgss-win-x86-vc14.2-0.3.7.89\bin\x86\Release` (acb2wavs). At the end of it, you should have something along this line

![Image of completed path](./path.png)

If for some reason, while running the script, something like `acb2wavs is not recognized as an internal or external command, operable program or batch file` appears, try adding an ending backlash ("\\") to the path (from `D:\libcgss-win-x86-vc14.2-0.3.7.89\bin\x86\Release` to `D:\libcgss-win-x86-vc14.2-0.3.7.89\bin\x86\Release\`)

If this still wasn't clear, you can contact me through Discord from [Priconne Unofficial Server](https://discord.gg/priconne), if you're not from the server, chances are I will just ignore your DM/friend req. My username is **mightyzanark**.


## Building

If you want to modify and build the program yourself, you will need:
- [Python 3.9.6](https://www.python.org/downloads/)
- Requests
- Pyinstaller
- PyCriCodecs

You can download and install the libraries by doing this command in your terminal
```
pip install -r requirements.txt
```

After installing those, you can just run the `build.bat` file under the scripts folder.
