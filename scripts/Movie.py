import os, requests, re, multiprocessing
import Constants
from concurrent.futures import ThreadPoolExecutor

name = []
hash = []

# Generates name and hash list for ThreadPoolExecutor and multiprocessing
def generate_list(mov_name, dir_name):
    # print(f'mov_name: {mov_name} | dir_name: {dir_name} | isdir: {os.path.isdir(dir_name)}')
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    # print(mov_name)
    with open(Constants.MOVIEMANIFEST, 'r') as m:
        for lines in m:
            l = lines.split(',')
            n = l[0].split('/')[-1]
            h = l[1]

            if re.fullmatch(mov_name, n):
                name.append(os.path.join(dir_name, n))
                hash.append(h)
    
    # return name, hash

# Downloads all video files that doesn't exist yet
def download_file(name: str, hash):
    # print(f'Filename is {name}')
    if not os.path.isfile(name) and not os.path.isfile(f'{name.split(".")[0]}.mp4'):
        print(f'Downloading {os.path.basename(name)}...')
        r = requests.get(f'{Constants.MOVIE_URL}/{hash[:2]}/{hash}').content
        with open(name, 'wb') as usm:
            usm.write(r)

    else:
        print(f'File [{os.path.basename(name)}] already exists')
    # return


# Converts all of the usm files to mp4 files
def convert_file(name: str):
    try:
        if not os.path.isfile(f'{name.split(".")[0]}.mp4'):
            os.system(f'UsmToolkit convert -c "{name}" -o "{os.path.dirname(name)}"')
    
        # else:
        #     print(f'File [.\\{str(name).split(".")[1]}.mp4] already exists')
    
    except Exception as e:
        print(f'An ERROR occured\n{e}')

    # return

# Main function to run
def movie():
    if not os.path.isfile(Constants.MOVIEMANIFEST):
        print("Please do DBCheck first before using this as the file needed to download stuff in this script is downloaded from DBCheck")
        input("Press ENTER to continue")

    else:
        mov_type = input("Select type: 'cutin' 'l2d' 'summon' 'event'\n")
        
        try:
            dir_name = Constants.MOVIE_TYPES['dir'][mov_type.strip()]
            mov_name = Constants.MOVIE_TYPES['name'][mov_type.strip()]
            generate_list(mov_name, dir_name)

        except:
            print("> INVALID TYPE! <\nCurrent types are only 'cutin', 'l2d', 'summon', or 'event'\n")
            input("Press ENTER to continue")
    
        else:
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

        finally:
            input(">> Download and conversion completed!\nPress ENTER to continue")
            name.clear()
            hash.clear()


# if __name__ == '__main__':
#     movie()