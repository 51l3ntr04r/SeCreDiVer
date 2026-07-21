from pathlib import Path
import json

# path to the blacklist file where revoked credential roots are stored
rev_F = Path('issuer/revokInfo/revo_reg.json')

def revCred(r_hex: str):
    #Adds a credential's  root hash to the revocated list.
    # open the file and load existing revoked entries
    with open(rev_F, "r") as jf_r:
        d = json.load(jf_r)
    
    rl = list()
    if "revoked" in d:
        rl = d["revoked"]
    
    #Add the new merkle root to the list
    rl.append(r_hex)
    
    # save updated list back to json file
    with open(rev_F, "w") as jf_w:
        json.dump({"revoked": rl}, jf_w)

def isRev(r_hex: str):
    # check whether this credential has been revoked
    # Open the registry
    with open(rev_F, "r") as jf_r:
        d = json.load(jf_r)
    # see if merkle root is in revoked list
    # if yes, credential is not valid 
    if "revoked" in d and r_hex in d["revoked"]:
        return True
    else:
        return False