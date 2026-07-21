from datetime import datetime, timezone, timedelta
from core.ecdsa import genKeys, sign, rsToDict
from core.ec import xyTob64
from core.merkle import mkTree, getRoot, bytToStr

class IssuerAuthority:
    #Represents an entity that has the authority to verify data 
    #and issue it as a trusted digital credential.   
    def __init__(self, name: str):
        # Setting up the identity of the Authority.
        self.name = name
        # Generate a unique Private Key (to sign) and Public Key (to share).
        kp = genKeys()
        self.priv_k = kp[0]
        self.publ_k = kp[1]

    def issueCred(self, holder: str, fields: dict[str, any], valDays: int):
        """Takes user data and turns it into a securely signed digital credential."""
        # 1.Convert dictionary items into a list of tuples.
        f_pairs = [(name, value) for name, value in fields.items()]
        
        # 2. Structure the data
        cred = [{'name': name, 'value': value, 'ftype': type(value).__name__} for name, value in f_pairs]
        
        # 3 Build the Merkle Tree and get the Root Hash.
        hash_tree = bytToStr(mkTree(f_pairs))
        root = getRoot(mkTree(f_pairs))
        r_hex = root.hex() # We use the Root Hash as the unique ID for the credential.

        # 4. creating the Signature by signing the root with the Authority's Private Key.
        # This proves the document came from 'self.name' and hasn't been damaged or tampered by anyone .
        sign_root = rsToDict(sign(root, self.priv_k))

        # 5. Set the timestamps for time of issue and expiry of credential.
        iss_tim = datetime.now(timezone.utc).isoformat()
        exp_tim = (datetime.now(timezone.utc) + timedelta(days=valDays)).isoformat()
        
        return {  # Everything the Holder needs for their digital wallet.
            'cred_id': r_hex,
            'issuer': self.name,
            'holder': holder,
            'fields': cred,
            'levels': hash_tree,
            'root': r_hex,
            'signature': sign_root,
            'issued_at': iss_tim,
            'expires_at': exp_tim,
            'issuer_public_key': xyTob64(self.publ_k)
        }
    
    def getPubK(self):    #Returns the Authority's public Key in a shareable format.
        return xyTob64(self.publ_k)