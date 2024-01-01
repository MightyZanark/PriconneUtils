import os
import re
import traceback
import subprocess
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

import requests
import PyCriCodecs as pcc

import Constants


def generate_list(mov_name: str, dir_name: str) -> tuple[list[str], list[str]]:
    """
    Generates name and hash list for ThreadPoolExecutor and multiprocessing
    """
    
    # print(f'mov_name: {mov_name} | dir_name: {dir_name} | isdir: {os.path.isdir(dir_name)}')
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    # print(mov_name)
    name = []
    hash = []
    with open(Constants.MOVIEMANIFEST, "r") as m:
        for lines in m:
            l = lines.split(",")
            n = l[0].split("/")[-1]
            h = l[1]

            if re.fullmatch(mov_name, n):
                name.append(os.path.join(dir_name, n))
                hash.append(h)
    
    return name, hash


def download_file(name: str, hash: str) -> None:
    """
    Downloads all video files that doesn't exist yet
    """

    # print(f'Filename is {name}')
    if not os.path.isfile(name) and not os.path.isfile(f'{name.split(".")[0]}.mp4'):
        print(f'Downloading [{os.path.basename(name)}]...')
        r = requests.get(f'{Constants.MOVIE_URL}/{hash[:2]}/{hash}').content
        with open(name, "wb") as usm:
            usm.write(r)

    # else:
    #     print(f'File [{os.path.basename(name)}] already exists')


def convert_file(name: str) -> None:
    """
    Converts all of the usm files to mp4 files
    """

    try:
        name_mp4 = name.split(".")[0] + ".mp4"
        if not os.path.isfile(name_mp4):
            filenames = extract(name, os.path.dirname(name))
            ffmpeg_combine = "ffmpeg -hide_banner -loglevel quiet -y "
            for fname in filenames[1:]:
                ffmpeg_combine += f'-i {fname} '
            
            ffmpeg_combine += name_mp4
            print(f'Converting [{os.path.basename(name)}]...')
            subprocess.run(ffmpeg_combine, check=True)

            # Unlink the usm_obj so the usm file can be removed
            # del usm_obj
            for file in filenames:
                os.remove(file)
    
    except subprocess.CalledProcessError:
        print("FFmpeg not found!")
        print("Please install FFmpeg first or make sure its in the PATH variable")
        input("Press ENTER to exit")
        exit(1)

    except NotImplementedError as nie:
        print(nie)

    except Exception:
        print(f'An ERROR occured\n{traceback.format_exc()}')


def extract(filename: str, dirname: str = "") -> list[str]:
    """
    Slightly modified extract() function from PyCriCodecs's usm.py
    to accomodate Priconne's USM\n
    Returns a list of all filenames inside of the USM
    """

    # Gets a table consisting of video/audio metadata
    usm = pcc.USM(filename)
    usm.demux()
    table = usm.get_metadata()[0]["CRIUSF_DIR_STREAM"]
    filenames: list[str] = []
    for obj in table:
        fname: str = obj["filename"][1]

        # Taken from PyCriCodecs' usm.py extract() method
        # Adjust filenames and/or paths to extract them into the current directory.
        if ":\\" in fname: # Absolute paths.
            fname = fname.split(":\\", 1)[1]
        elif ":/" in fname: # Absolute paths.
            fname = fname.split(":/", 1)[1]
        elif ":"+os.sep in fname: # Absolute paths.
            fname = fname.split(":"+os.sep, 1)[1]
        elif ".."+os.sep in fname: # Relative paths.
            fname = fname.rsplit(".."+os.sep, 1)[1]
        elif "../" in fname: # Relative paths.
            fname = fname.rsplit("../", 1)[1]
        elif "..\\" in fname: # Relative paths.
            fname = fname.rsplit("..\\", 1)[1]
        fname = ''.join(x for x in fname if x not in ':?*<>|"') # removes illegal characters.

        fname = os.path.join(dirname, fname)
        if fname not in filenames:
            filenames.append(fname)
    
    keys = list(usm.output.keys())
    while (idx := len(filenames[1:])) < len(usm.output.keys()):
        fname: str = filenames[0].split(".")[0]
        if "SFV" in keys[idx]:
            fname += ".avi"

        elif "SFA" in keys[idx]:
            fname += ".wav"

        else:
            raise NotImplementedError(
                f'Unknown type of data: {keys[idx]}\n'
                f'Header: {list(usm.output.values())[idx][:4]}'
            )
        
        filenames.append(fname)

    for i, (k, data) in enumerate(usm.output.items()):
        try:
            if "SFV" in k:
                with open(filenames[i+1], "wb") as out:
                    out.write(data)
            
            elif "SFA" in k:
                audio = pcc.ADX(data)
                with open(filenames[i+1], "wb") as out:
                    out.write(audio.decode())
            
            else:
                raise NotImplementedError(f'Unknown type of data: {k}\nHeader: {data[:4]}')

        except IndexError:
            print(
                'Filenames amount < Expected output items\n'
                f'Filenames = {filenames}\n'
                f'Expected output = {list(usm.output.keys())}\n'
            )
        
    return filenames


def movie() -> None:
    """
    Runs the Movie download and conversion logic
    """

    if not os.path.isfile(Constants.MOVIEMANIFEST):
        print(
            "Please do DBCheck first before using this "
            "as the file needed to download stuff in this script "
            "is downloaded from DBCheck"
        )
        input("Press ENTER to continue")
        return

    else:
        print("Select type: (write the number)")
        print("1. cutin\n2. l2d\n3. summon\n4. event")
        mov_type = input(">> ").lower().strip()
        
        try:
            mov_dict = {"1": "cutin", "2": "l2d", "3": "summon", "4": "event"}
            mov_type = mov_dict[mov_type]
            dir_name = Constants.MOVIE_TYPES["dir"][mov_type]
            mov_name = Constants.MOVIE_TYPES["name"][mov_type]
            name, hash = generate_list(mov_name, dir_name)

        except KeyError:
            print("> INVALID TYPE! <")
            print("Current types are only 'cutin', 'l2d', 'summon', or 'event'\n")
            input("Press ENTER to continue")
            return
    
        else:
            # ThreadPoolExecutor and multiprocessing makes it so the 
            # downloading and converting of a file doesn't happen 1 by 1
            # Instead, a few files are downloaded at a time and after all 
            # of those files finished downloading, they get converted a 
            # few files at the same time as well
            # The number of files downloaded or converted at a time will 
            # depend on your system and download speed (for download)
            with ThreadPoolExecutor() as thread:
                thread.map(download_file, name, hash)
                thread.shutdown(wait=True)

            with multiprocessing.Pool() as pool:
                pool.map(convert_file, name)
                pool.terminate()

        input(">> Download and conversion completed!\nPress ENTER to continue")


if __name__ == "__main__":
    movie()