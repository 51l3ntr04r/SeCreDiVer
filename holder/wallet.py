import json
import os
from pathlib import Path

# path where wallet files are stored
p = Path('holder/wallet')

def save_cred(cred_dict: dict):
    #Saves a new credential to the wallet.
    # uses cred_id as filename (eg., ID123.json)
    with open(p / (cred_dict['cred_id'] + '.json'), "w") as f:
        # json.dump converts the dictionary into JSON format.
        json.dump(cred_dict, f)

def load_cred(cred_id: str):
   # get credential from wallet using its ID
    # check if file exists to avoid errors
    file_name = p / (cred_id + '.json')
    if file_name in p.iterdir():
        with open(file_name, "r") as f:
            # json.load change the JSON text into a dictionary.
            return json.load(f)
        
def list_cred():
    #Shows a list of everything inside the wallet.
    #It goes through the files and removes '.json' to show only IDs.
    return [str(f.name).replace('.json', '') for f in p.iterdir()]

def del_cred(cred_id: str):
    #Deletes a credential from the wallet .
    if p / (cred_id + '.json') in p.iterdir():
        # os.remove permanently deletes the file from the storage.
        os.remove(p / (cred_id + '.json'))