import os, requests, json

cur_dir = os.getcwd()
max_test = 20
test_multi = 10
conf = r'.\config.json'
db_dir = r'.\database'

def update_db():
    # Checks if database folder exist, if it doesn't then create one
    if not os.path.isdir(db_dir):
        os.mkdir(db_dir)

    print('Checking for database updates...')
    with open(conf, 'r+') as j:
        c = json.load(j)
        version = int(c["TruthVersion"])
        assetmanifest = str(c["assetmanifest"])
        i = 1

        # While loop to check for new versions
        while i <= max_test:
            guess = version + (i * test_multi)
            r = requests.get(assetmanifest.replace('version', str(guess)))
            if r.status_code == 200:
                print(f'[{guess}] is a valid new version. Checking for more...')
                version = guess
                i = 1
            else:
                i += 1
        
        # Checks if the TruthVersion is the same as in the latest_ver.json
        if version == int(c["TruthVersion"]):
            
            # Checks if master.db or manifests file exist. If it doesn't, then download them
            # If anyone has a better way to approach this, you can do a pull request or make a suggestion from the "Issues" tab
            while True:
                if not os.path.isfile(f'{db_dir}\\master.db'):
                    print(f'No database file detected, downloading the latest: [{version}]')
                    download_manifest('db')
                elif not os.path.isfile(f'{db_dir}\\moviemanifest'):
                    print("No moviemanifest file detected, downloading...")
                    download_manifest('movie')
                elif not os.path.isfile(f'{db_dir}\\sound2manifest'):
                    print("No sound2manifest file detected, downloading...")
                    download_manifest('sound')
                else:
                    print("> Database is up to date!")
                    break

        else:
            # Updates config.json
            r = requests.get(str(c["masterdata"]).replace('version', str(version))).content
            l = str(r).split(',')
            hash = l[1]
            c["TruthVersion"] = version
            c["hash"] = hash
            j.seek(0)
            json.dump(c, j, indent=1)

            # Downloads the new database alongside manifests
            print(f'New version available: [{version}], updating database...')
            download_manifest('db')
            download_manifest('sound')
            download_manifest('movie')
            print("> Update completed!")

# Downloads .db and sound/movie manifest to use for L2D, BGM extraction, etc.
def download_manifest(type):
    with open(conf, 'r') as f:
        data = json.load(f)
        t = str(data[type])
        hash = data["hash"]
        manifest_name = t.split("/")[-1]
        ver = str(data["TruthVersion"])
        
        if type == 'db':
            print("Downloading database...")
            database = requests.get(f'{t}/{hash[:2]}/{hash}').content
            with open('master.cdb', 'wb') as cdb:
                cdb.write(database)
            os.system(f'Coneshell_call.exe -cdb master.cdb "{db_dir}\\master.db"')
            os.remove('master.cdb')
            print("> Finished downloading database!\n")

        else:
            print(f'Downloading {manifest_name}...')
            manifest = requests.get(t.replace('version',ver)).content
            with open(f'{db_dir}\\{manifest_name}', 'wb') as m:
                m.write(manifest)
            print("> Download completed!\n")

if __name__ == '__main__':
    update_db()