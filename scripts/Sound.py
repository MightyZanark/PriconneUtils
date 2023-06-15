import os
import re
import shutil
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

import requests

import Constants

name = []
hash = []

def generate_list(snd_name, snd_dir):
    if not os.path.isdir(snd_dir):
        os.makedirs(snd_dir)

    with open(Constants.SOUNDMANIFEST, 'r') as f:
        for lines in f:
            l = lines.split(',')
            n = l[0].split('/')[-1]
            h = l[1]

            if re.fullmatch(snd_name, n):
                # print(f'Name is [{n}]')
                name.append(os.path.join(snd_dir, n))
                hash.append(h)


def download_file(name: str, hash):
    dirName = os.path.dirname(name)
    realFileName = os.path.basename(name)
    nameCheck = re.compile(f'{realFileName.split(".")[0]}.+?m4a')
    checked = check_file(nameCheck, dirName)

    if not os.path.isfile(name) and checked is None:
        print(f'Downloading {name}...')
        r = requests.get(f'{Constants.SOUND_URL}/{hash[:2]}/{hash}').content
        with open(name, 'wb') as f:
            f.write(r)

    else:
        print(f'File [{realFileName}] already exists')

def convert_file(name: str):
    dir_name = os.path.dirname(name)
    realFilename = os.path.basename(name)
    
    acbUnpackDir = os.path.join(dir_name, f'_acb_{realFilename}')
    acbInternal = os.path.join(acbUnpackDir, 'internal')
    acbExternal = os.path.join(acbUnpackDir, 'external')
    
    nameCheck = re.compile(f'{realFilename.split(".")[0]}.+?m4a')
    checked = check_file(nameCheck, dir_name)

    if checked is None:
        # print(f'Name is {checked}')
        # print(f'Filename: {realFilename} | Checkfile: {check_file(nameCheck, dir_name)}')
        try:
            if name.endswith('.acb') and os.path.isfile(name):
                os.system(f'acb2wavs "{name}" -b 00000000 -a 0030D9E8 -n')
                os.remove(name)
                os.remove(f'{name.split(".")[0]}.awb')
            
                if os.path.isdir(acbInternal):
                    for waveFile in os.listdir(acbInternal):
                        m4aFile = f'{waveFile.split(".")[0]}.m4a'
                        # print(f'Abspath waveFile: {os.path.abspath(waveFile)} | Abspath m4aFile: {os.path.abspath(m4aFile)}')
                        print(f'Converting {waveFile} to {m4aFile}...')
                        os.system('ffmpeg -hide_banner -loglevel quiet -y '
                        f'-i "{os.path.abspath(os.path.join(acbInternal, waveFile))}" -vbr 5 -movflags faststart '
                        f'"{os.path.abspath(os.path.join(dir_name, m4aFile))}"')
                
                elif os.path.isdir(acbExternal):
                    for waveFile in os.listdir(acbExternal):
                        m4aFile = f'{waveFile.split(".")[0]}.m4a'
                        print(f'Converting {waveFile} to {m4aFile}...')
                        os.system('ffmpeg -hide_banner -loglevel quiet -y '
                        f'-i "{os.path.abspath(os.path.join(acbExternal, waveFile))}" -vbr 5 -movflags faststart '
                        f'"{os.path.abspath(os.path.join(dir_name, m4aFile))}"')
            
                shutil.rmtree(acbUnpackDir)
                print(">>> Conversion done!")
        
        except Exception as e:
            print(f"An ERROR occured\n{e}")


def check_file(fn, fd):
    for file in os.listdir(fd):
        a: re.Match = re.search(fn, file)
        if a: 
            return a.group()

def sound():
    if not os.path.isfile(Constants.SOUNDMANIFEST):
        print("Please do DBCheck first before using this as the file needed to download stuff in this script is downloaded from DBCheck")
        input("Press ENTER to continue")

    else:
        snd_type = input("Select sound type: bgm\n")

        try:
            snd_name = Constants.SOUND_TYPES['name'][snd_type.strip()]
            snd_dir = Constants.SOUND_TYPES['dir'][snd_type.strip()]
            generate_list(snd_name, snd_dir)

        except:
            print("> INVALID TYPE! <\nCurrent types are only 'bgm'\n")
            input("Press ENTER to continue")

        else:
            with ThreadPoolExecutor() as thread:
                thread.map(download_file, name, hash)
                thread.shutdown(wait=True)
            
            with multiprocessing.Pool() as pool:
                pool.map(convert_file, name)
                pool.terminate()

        finally:
            input(">> Download and conversion completed!\nPress ENTER to continue")
            name.clear()
            hash.clear()

# if __name__ == '__main__':
#     sound()