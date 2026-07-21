import json
import os
from pathlib import Path

# Define the location of the Digital Wallet on the computer.
p = Path('holder/wallet')

def save_cred(cred_dict: dict):
    """   Saves a new credential to the wallet.
    It takes the credential ID and uses it as the filename (e.g., 'ID123.json')."""
    with open(p / (cred_dict['cred_id'] + '.json'), "w") as f:
        # json.dump converts the Python dictionary into a text-based JSON format.
        json.dump(cred_dict, f)

def load_cred(cred_id: str):
    """Retrieves a specific credential from the wallet by its ID.
    It first checks if the file actually exists to prevent the app from crashing.    """
    file_name = p / (cred_id + '.json')
    if file_name in p.iterdir():
        with open(file_name, "r") as f:
            # json.load turns the JSON text back into a Python dictionary.
            return json.load(f)
        
def list_cred():
    """ Shows a list of everything inside the wallet.
    It loops through the files and removes '.json' so the user only sees the IDs.   """
    return [str(f.name).replace('.json', '') for f in p.iterdir()]

def del_cred(cred_id: str):
    """   Deletes a credential from the wallet (like revoking or discarding an old ID).   """
    if p / (cred_id + '.json') in p.iterdir():
        # os.remove permanently deletes the file from the storage.
        os.remove(p / (cred_id + '.json'))