import os, requests, json

cur_dir = os.getcwd()
max_test = 20
test_multi = 10
json_file = r'.\latest_ver.json'

def update_db():
    print('Checking for database updates...')
    with open(json_file, 'r+') as j:
        latest = json.load(j)
        version = int(latest["TruthVersion"])
        i = 1
        while i <= max_test:
            guess = version + (i * test_multi)
            r = requests.get(f'http://prd-priconne-redive.akamaized.net/dl/Resources/{guess}/Jpn/AssetBundles/Windows/manifest/manifest_assetmanifest')
            if r.status_code == 200:
                print(f'[{guess}] is a valid new version. Checking for more...')
                version = guess
                i = 1
            else:
                i += 1
        
        r = requests.get(f'http://prd-priconne-redive.akamaized.net/dl/Resources/{version}/Jpn/AssetBundles/Windows/manifest/masterdata_assetmanifest').content
        l = str(r).split(',')
        hash = l[1]
        
        if version == int(latest["TruthVersion"]):
            if not os.path.isfile('master.db'):
                print(f'No database file detected, downloading the latest: [{version}]')
                download_db(hash)
                print("> Finished downloading the latest database!")
            else:
                print("> Database is up to date!")
        else:
            print(f'New version available: [{version}], updating database...')
            download_db(hash)
            latest = {"TruthVersion": version, "hash": hash}
            j.seek(0)
            json.dump(latest, j)
            print("> Update completed!")
        
def download_db(hash):
    database = requests.get(f'http://prd-priconne-redive.akamaized.net/dl/pool/AssetBundles/{hash[:2]}/{hash}').content
    with open('master.cdb', 'wb') as cdb:
        cdb.write(database)
    os.system(f'Coneshell_call.exe -cdb master.cdb master.db')
    os.remove('master.cdb')

if __name__ == '__main__':
    update_db()