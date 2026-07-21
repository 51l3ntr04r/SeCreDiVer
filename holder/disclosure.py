from core.merkle import getProof, mkTree

def showCred(cred: dict[str, any], toShow: list[str]):
    # selective disclosure part
    # take full credential and only show selected fields
    #gives partial information that can still be mathematically verified.
    shol = list() # The Revealed list is the list what the verifier will see.
    hid = dict()  # The Hidden dictionary: Only hashes, no actual data.

# rebuild the full Merkle tree from all fields
# needed to generate proofs for selected data
    ht = mkTree([(cred['fields'][i]['name'], cred['fields'][i]['value']) for i in range(len(cred['fields']))])

    for i in range(len(cred['fields'])):
        field_name = cred['fields'][i]['name']
        
        # 2. Case 1 - The user wants to reveal this field (eg., 'Age').
        if field_name in toShow:
            shol.append({
                'name': field_name,
                'value': cred['fields'][i]['value'],
                'ftype': cred['fields'][i]['ftype'],
                'index': i,
        # add proof path so verifier can connect this field
        # back to the original Merkle root
                'proof': [[elem[0].hex(), elem[1]] for elem in getProof(ht, i)]
            })
        
        # 3.  case 2 - The user wants to keep this field secret (eg , religion).
        else:
            # We only share the leaf hash. # verifier can still do the tree check without seeing real data
            
            hid[field_name] = ht[0][i].hex()

    # 4. Return the data which contains disclosed field, signature etc. without the hidden field which is then sent to the verifier.
    return {
        'issuer_public_key': cred['issuer_public_key'],
        'root': cred['root'],
        'signature': cred['signature'],
        'issued_at': cred['issued_at'],
        'expires_at': cred['expires_at'],
        'revealed': shol,
        'hidden': hid
    }