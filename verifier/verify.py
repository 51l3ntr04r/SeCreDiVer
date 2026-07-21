from core.ec import xyFromb64
from core.ecdsa import dictToRS, verify
from datetime import datetime, timezone
from core.merkle import verifyProof
from issuer.revocation import isRev

def verifyDisc(disc: dict):
   # verify disclosed credential using multiple checks
    # returns (True/False, message)
# decode values into something we can use
    q = xyFromb64(disc['issuer_public_key']) # Public Key
    s = dictToRS(disc['signature'])          # Signature (r, s)
    r_hex = disc['root']                     # Merkle Root in hex
    r = bytes.fromhex(r_hex)                 # Merkle Root in bytes

    # check if credential has expired
    if datetime.now(timezone.utc) > datetime.fromisoformat(disc['expires_at']):
        return (False, 'Credential has expired !')

    #verify merkle proofs for each revealed field
    # if any proof doesn't match the root, data is modified
    for d in disc['revealed']:
        # convert proof from hex to bytes
        pf = [(bytes.fromhex(n), side) for (n, side) in d['proof']]
        if not verifyProof(d['name'], d['value'], pf, r):
            return (False, 'Invalid proof for consistency !')

    # check if signature is valid using public key
    # ensures the data was actually signed by the issuer
    if not verify(r, s, q):
        return (False, 'Not authenticated by the institution !')

    #check if this credential was revoked
    # if found in registry, it should not be trusted
    if isRev(r_hex):
        return (False, 'The credentials have been revoked by the institution !')

    # all checks passed
    return (True, 'Valid credentials !!')