import hashlib

def hash_bytes(data: bytes):
    #Returns the raw 32-byte SHA-256 hash of any input.
    #.digest() is used here to get raw binary instead of a hex string.  
    return hashlib.sha256(data).digest()

def hash_leaf(enc_byt: bytes):
    # hash one field (like Name or GPA)
# doing it per field helps with selective disclosure later
# ex: b'GPA:float:8.21' -> 32-byte hash            
    return hashlib.sha256(enc_byt).digest()

def hash_node(left: bytes, right: bytes):
    # combine two hashes and hash again
# if any child changes, parent hash changes too
# parent = sha256(left + right)  (used to build node)          
    return hashlib.sha256(left + right).digest()