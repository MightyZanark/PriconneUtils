import os
import json
from typing import Any

import requests
# from tqdm import tqdm

import Constants

def update_db() -> None:
    """Updates the db if there is an update"""

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


def download_manifest(type: str) -> None:
    """Downloads db or manifest files"""

    with open(Constants.CONFIG_FILE, 'r') as f:
        data: dict[str, Any] = json.load(f)
        t: str = data[type]
        hash: str = data["hash"]
        manifest_name: str = t.split("/")[-1]
        ver = str(data["TruthVersion"])
        
        if type == 'db':
            print("Downloading database...")
            database = requests.get(f'{t}/{hash[:2]}/{hash}').content
            with open('master.cdb', 'wb') as cdb:
                cdb.write(database)
            os.system(f'Coneshell_call.exe -cdb master.cdb "{os.path.join(Constants.DB_DIR, "master.db")}"')
            os.remove('master.cdb')
            print("> Finished downloading database!\n")

        else:
            print(f'Downloading {manifest_name}...')
            manifest = requests.get(t.replace('version', ver)).content
            with open(os.path.join(Constants.DB_DIR, manifest_name), 'wb') as m:
                m.write(manifest)
            print(f"> Finished downloading {manifest_name}!\n")


def check_update():
    """Checks if there is an update and updates config.json"""

    with open(Constants.CONFIG_FILE, 'r+') as j:
        c: dict[str, Any] = json.load(j)
        version: int = c["TruthVersion"]
        assetmanifest: str = c["assetmanifest"]
        i = 1
        # pbar = tqdm(total=Constants.MAX_TEST, leave=False)

        # While loop to check for new versions
        while i <= Constants.MAX_TEST:
            guess = version + (i * Constants.TEST_MULTIPLIER)
            r = requests.get(assetmanifest.replace('version', str(guess)))
            if r.status_code == 200:
                # pbar.close()
                print(f'[{guess}] is a valid new version. Checking for more...')
                version = guess
                i = 1
                # pbar = tqdm(total=Constants.MAX_TEST, leave=False)
            
            else:
                i += 1
                # pbar.update(1)
        # pbar.close()

        # Checks if the TruthVersion is the same as in config.json
        if version == c["TruthVersion"]:
            print('> Database version is up to date!\n')

        else:
            print(f'New version available: [{version}], updating database...')
            # Updates config.json
            r = requests.get(str(c["masterdata"]).replace('version', str(version))).content
            l = str(r).split(',')
            hash = l[2]
            c["TruthVersion"] = version
            c["hash"] = hash
            j.seek(0)
            json.dump(c, j, indent=1)
    
    # print('>> Update check completed!\n')


if __name__ == '__main__':
    update_db()