import os, requests, re, multiprocessing
from concurrent.futures import ThreadPoolExecutor

manifest_path = r'.\database\moviemanifest'
movie_url = 'http://prd-priconne-redive.akamaized.net/dl/pool/Movie'

l2d_dir = r'.\movie\l2d'
l2d_name = re.compile('character_\d+_000002\.usm')

cutin_dir = r'.\movie\cutin'
cutin_name = re.compile('cutin_\d+\.usm')

summon_dir = r'.\movie\summon'
summon_name = re.compile('character_\d+_000001\.usm')

event_dir = r'.\movie\event'
event_name = re.compile('story_5\d{5}[7-9]0[1-2]\.usm')

mov = {
    'dir': {
        'cutin': cutin_dir,
        'l2d': l2d_dir,
        'summon': summon_dir,
        'event': event_dir
    },
    'name': {
        'cutin': cutin_name,
        'l2d': l2d_name,
        'summon': summon_name,
        'event': event_name
    }
}

name = []
hash = []


# Generates name and hash list for ThreadPoolExecutor and multiprocessing
def generate_list(mov_name: str, dir_name):
    # print(f'mov_name: {mov_name} | dir_name: {dir_name} | isdir: {os.path.isdir(dir_name)}')
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    # print(mov_name)
    with open(manifest_path, 'r') as m:
        for lines in m:
            l = lines.split(',')
            n = l[0].split('/')[-1]
            h = l[1]

            if re.fullmatch(mov_name, n):
                name.append(f'{dir_name}\\{n}')
                hash.append(h)
    
    # return name, hash

# Downloads all video files that doesn't exist yet
def download_file(name, hash):
    # print(f'Filename is {name}')
    if not os.path.isfile(name) and not os.path.isfile(f'.\\{str(name).split(".")[1]}.mp4'):
        print(f'Downloading {name}...')
        r = requests.get(f'{movie_url}/{hash[:2]}/{hash}').content
        with open(name, 'wb') as usm:
            usm.write(r)

    else:
        print(f'File [{name}] already exists')


# Converts all of the usm files to mp4 files
def convert_file(name):
    try:
        if not os.path.isfile(f'.\\{str(name).split(".")[1]}.mp4'):
            os.system(f'UsmToolkit convert -c "{name}" -o "{os.path.dirname(name)}"')
    
        # else:
        #     print(f'File [.\\{str(name).split(".")[1]}.mp4] already exists')
    
    except Exception as e:
        print(f'An ERROR occured\n{e}')


# Main function to run
def main():
    if not os.path.isfile(manifest_path):
        print("Please do DBCheck first before using this as the file needed to download stuff in this script is downloaded from DBCheck")
        input("Press ENTER to exit this window")

    else:
        mov_type = input("Select type: 'cutin' 'l2d' 'summon' 'event'\n")
        
        try:
            dir_name = mov['dir'][mov_type.strip()]
            mov_name = mov['name'][mov_type.strip()]
            generate_list(mov_name, dir_name)

            # ThreadPoolExecutor and multiprocessing makes it so the downloading and converting of a file doesn't happen 1 by 1
            # Instead, a few files are downloaded at a time and after all of those files finished downloading, they get
            # converted a few files at the same time as well
            # The number of files downloaded or converted at a time will depend on your system and download speed (for download)
            with ThreadPoolExecutor() as thread:
                thread.map(download_file, name, hash)
                thread.shutdown(wait=True)

            with multiprocessing.Pool() as pool:
                pool.map(convert_file, name)
                pool.terminate()

            input(">> Download and conversion completed!\nPress ENTER to exit this window")

        except:
            print("> INVALID TYPE! <\nCurrent types are only 'cutin', 'l2d', 'summon', or 'event'\n")
            input("Press ENTER to exit this window")
        

if __name__ == '__main__':
    main()