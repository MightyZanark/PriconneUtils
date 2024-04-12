import os
import re
import sqlite3
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
    
    names = []
    hashes = []
    with open(Constants.MOVIEMANIFEST, "r") as m:
        for lines in m:
            l = lines.split(",")
            n = l[0].split("/")[-1]
            h = l[2]

            if re.fullmatch(mov_name, n):
                names.append(os.path.join(dir_name, n))
                hashes.append(h)
    
    return names, hashes


def get_filename_and_hash(mov_name: re.Pattern, id: str) -> tuple[str] | bool:
    """Gets the filename and hash for a specific unit id"""

    with open(Constants.MOVIEMANIFEST, "r") as m:
        for lines in m:
            l = lines.split(",")
            name = l[0].split("/")[-1]
            hash = l[1]

            if re.fullmatch(mov_name, name) and id in name:
                return name, hash
    
    return False


def download_file(name: str, hash: str) -> None:
    """
    Downloads all video files that doesn't exist yet
    """

    if not os.path.isfile(name) and not os.path.isfile(f'{name.split(".")[0]}.mp4'):
        print(f'Downloading [{os.path.basename(name)}]...')
        r = requests.get(f'{Constants.MOVIE_URL}/{hash[:2]}/{hash}').content
        with open(name, "wb") as usm:
            usm.write(r)


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
                audio = pcc.ADX.decode(data)
                with open(filenames[i+1], "wb") as out:
                    out.write(audio)
            
            else:
                raise NotImplementedError(f'Unknown type of data: {k}\nHeader: {data[:4]}')

        except IndexError:
            print(
                'Filenames amount < Expected output items\n'
                f'Filenames = {filenames}\n'
                f'Expected output = {list(usm.output.keys())}\n'
            )
        
    return filenames


def download_all(mov_name: str, dir_name: str) -> None:
    """Downloads all the usm of a movie type and converts them to mp4"""

    names, hashes = generate_list(mov_name, dir_name)

    with ThreadPoolExecutor() as thread:
        thread.map(download_file, names, hashes)
        thread.shutdown(wait=True)

    with multiprocessing.Pool() as pool:
        pool.map(convert_file, names)
        pool.terminate()


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

    print("Select type: (write the number)")
    print("1. cutin\n2. l2d\n3. summon\n4. event")
    mov_type = input(">> ").lower().strip()
    
    try:
        mov_dict = {"1": "cutin", "2": "l2d", "3": "summon", "4": "event"}
        mov_type = mov_dict[mov_type]
        dir_name = Constants.MOVIE_TYPES["dir"][mov_type]
        mov_name = Constants.MOVIE_TYPES["name"][mov_type]

    except KeyError:
        print("> INVALID TYPE! <")
        print("Current types are only 'cutin' (1), 'l2d' (2), 'summon' (3), or 'event' (4)\n")
        input("Press ENTER to continue")
        return

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    # if mov_type == 'event':
    download_all(mov_name, dir_name)

    # Does not currently work because db is obfuscated
    # else:
    #     select = input(f"Download all {mov_type}? (y/N, default: N)\n").strip().lower()

    #     if select and (select == 'y' or select[0] == 'y'):
    #         download_all(mov_name, dir_name)

    #     else:
    #         con = sqlite3.connect(os.path.join(Constants.DB_DIR, 'master.db'))
    #         cur = con.cursor()
    #         query = cur.execute(
    #                         "SELECT unit_name, unit_id "
    #                         "FROM unit_data "
    #                         "WHERE unit_id < 190000 AND move_speed = 450 AND unit_id != 170101"
    #                     ).fetchall()
    #         names = [q[0].strip() for q in query]
    #         ids = [q[1] for q in query]
    #         name_lst = ''
    #         for idx, name in enumerate(names, 1):
    #             offset = 15 - len(name)
    #             name += u'\u3000' * offset
    #             idx_str = str(idx) + "."
    #             name_lst += f"{idx_str:<4} {name}"
    #             print(f"{idx_str:<4} {name}", end='')
    #             if idx % 3 == 0:
    #                 name_lst += '\n'
    #                 print()
    #         print()

    #         correct = False
    #         while not correct:
    #             chara = input("Enter the character number: ").strip()
    #             names_len = len(names)
    #             while not chara.isdigit() or int(chara) < 1 or int(chara) > names_len:
    #                 chara = input(f"Invalid number! Please enter a number between 1-{names_len}: ")
                
    #             chara = int(chara)-1
    #             name = names[chara]
    #             id = ids[chara]

    #             correct = input(f"Is {name} the right character? (y/N, default: y)\n").strip()
    #             correct = True if correct != 'n' or correct[0] != 'n' else False
            
    #         found = get_filename_and_hash(mov_name, str(id)[:-2])
    #         if not found:
    #             print(f"{name} does not have a {mov_type}")
            
    #         else:
    #             name, hash = found
    #             name = os.path.join(dir_name, name)
    #             download_file(name, hash)
    #             convert_file(name)

    input(">> Download and conversion completed!\nPress ENTER to continue")


if __name__ == "__main__":
    movie()