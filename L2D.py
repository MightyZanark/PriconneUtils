import os, requests, re

manifest_path = r'.\database\moviemanifest'
l2d_dir = r'.\l2d'
movie_url = 'http://prd-priconne-redive.akamaized.net/dl/pool/Movie'
l2d_name = re.compile('character_\d+_000002\.usm')

def download_l2d():
    if not os.path.isdir(l2d_dir):
        os.mkdir(l2d_dir)
        
    with open(manifest_path, 'r') as m:

        #Iterates through all the lines in moviemanifest
        for lines in m:
            l = lines.split(',')
            name = l[0].split('/')[-1]
            hash = l[1]

            #Checks if the file name is for L2D or not and also if the file already exists or not
            #If the file name is correct and the file doesn't exist yet, then download it
            if re.fullmatch(l2d_name, name) and not os.path.isfile(f'{l2d_dir}\\{name.split(".")[0]}.mp4'):
                print(f'Downloading [{name}]')
                r = requests.get(f'{movie_url}/{hash[:2]}/{hash}').content
                with open(os.path.join(l2d_dir, name), 'wb') as usm:
                    usm.write(r)
                
                #Calls UsmToolkit to convert the .usm file to a normal .mp4 file
                os.system(f'UsmToolkit convert -c "{l2d_dir}\\{name}" -o {l2d_dir}')
                print(f'> Successfully converted [{name}] to [{name.split(".")[0]}.mp4]\n')


download_l2d()
