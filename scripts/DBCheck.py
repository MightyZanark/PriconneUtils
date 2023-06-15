import os
import json

import requests

import Constants

# Function to update the db if there is one
def update_db():
    # Checks if database folder exist, if it doesn't then create one
    if not os.path.isdir(Constants.DB_DIR):
        os.mkdir(Constants.DB_DIR)

    print('Checking for database updates...')
    check_update()

    # Downloads the new database alongside manifests
    # print('Downloading database and manifests...')
    download_manifest('db')
    download_manifest('sound')
    download_manifest('movie')
    print(">> Update completed!")

# Downloads .db and sound/movie manifest to use for L2D, BGM extraction, etc.
def download_manifest(type):
    with open(Constants.CONFIG_FILE, 'r') as f:
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
            os.system(f'Coneshell_call.exe -cdb master.cdb "{Constants.DB_DIR}\\master.db"')
            os.remove('master.cdb')
            print("> Finished downloading database!\n")

        else:
            print(f'Downloading {manifest_name}...')
            manifest = requests.get(t.replace('version', ver)).content
            with open(os.path.join(Constants.DB_DIR, manifest_name), 'wb') as m:
                m.write(manifest)
            print("> Download completed!\n")

# Function to check for DB updates and to update config.json if there is an update
def check_update():
    with open(Constants.CONFIG_FILE, 'r+') as j:
        c = json.load(j)
        version = int(c["TruthVersion"])
        assetmanifest = str(c["assetmanifest"])
        i = 1

        # While loop to check for new versions
        while i <= Constants.MAX_TEST:
            guess = version + (i * Constants.TEST_MULTIPLIER)
            r = requests.get(assetmanifest.replace('version', str(guess)))
            if r.status_code == 200:
                print(f'[{guess}] is a valid new version. Checking for more...')
                version = guess
                i = 1
            else:
                i += 1
        
        # Checks if the TruthVersion is the same as in the latest_ver.json
        if version == int(c["TruthVersion"]):
            print('> Database version is up to date!\n')

        else:
            print(f'New version available: [{version}], updating database...')
            # Updates config.json
            r = requests.get(str(c["masterdata"]).replace('version', str(version))).content
            l = str(r).split(',')
            hash = l[1]
            c["TruthVersion"] = version
            c["hash"] = hash
            j.seek(0)
            json.dump(c, j, indent=1)
    
    # print('>> Update check completed!\n')


# if __name__ == '__main__':
#     update_db()