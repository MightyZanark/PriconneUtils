import os, requests, re, shutil, multiprocessing
from concurrent.futures import ThreadPoolExecutor

manifest_path = r'.\database\sound2manifest'
sound_url = 'http://prd-priconne-redive.akamaized.net/dl/pool/Sound'

bgm_dir = r'.\sound\bgm'
bgm_name = re.compile('bgm_.+\.(acb||awb)')

sound = {
    'dir': {
        'bgm': bgm_dir
    },
    'name': {
        'bgm': bgm_name
    }
}

name = []
hash = []

def generate_list(snd_name, snd_dir):
    if not os.path.isdir(snd_dir):
        os.makedirs(snd_dir)

    with open(manifest_path, 'r') as f:
        for lines in f:
            l = lines.split(',')
            n = l[0].split('/')[-1]
            h = l[1]

            if re.fullmatch(snd_name, n):
                # print(f'Name is [{n}]')
                name.append(f'{snd_dir}\\{n}')
                hash.append(h)


def download_file(name: str, hash):
    dirName = os.path.dirname(name)
    realFileName = name.split('\\')[-1]
    nameCheck = re.compile(f'{realFileName.split(".")[0]}.+?m4a')
    checked = check_file(nameCheck, dirName)

    if not os.path.isfile(name) and checked is None:
        print(f'Downloading {name}...')
        r = requests.get(f'{sound_url}/{hash[:2]}/{hash}').content
        with open(name, 'wb') as f:
            f.write(r)

    # else:
    #     print(f'File {name} already exists')

def convert_file(name: str):
    dir_name = os.path.dirname(name)
    realFilename = name.split('\\')[-1]
    
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
                os.remove(f'.\\{name.split(".")[1]}.awb')
            
                if os.path.isdir(acbInternal):
                    for waveFile in os.listdir(acbInternal):
                        m4aFile = f'{waveFile.split(".")[0]}.m4a'
                        print(f'Abspath waveFile: {os.path.abspath(waveFile)} | Abspath m4aFile: {os.path.abspath(m4aFile)}')
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
        a = re.search(fn, file)
        if a: 
            return a.group()

def main():
    if not os.path.isfile(manifest_path):
        print("Please do DBCheck first before using this as the file needed to download stuff in this script is downloaded from DBCheck")
        input("Press ENTER to exit this window")

    else:
        snd_type = input("Select sound type: bgm\n")

        try:
            snd_name = sound['name'][snd_type.strip()]
            snd_dir = sound['dir'][snd_type.strip()]
            generate_list(snd_name, snd_dir)

            with ThreadPoolExecutor() as thread:
                thread.map(download_file, name, hash)
                thread.shutdown(wait=True)
            
            with multiprocessing.Pool() as pool:
                pool.map(convert_file, name)
                pool.terminate()

            input(">> Download and conversion completed!\nPress ENTER to exit this window")

        except:
            print("> INVALID TYPE! <\nCurrent types are only 'bgm'\n")
            input("Press ENTER to exit this window")

if __name__ == '__main__':
    main()