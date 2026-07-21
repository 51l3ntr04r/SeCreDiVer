from hashlib import sha256
import secrets
from core.ec import scalMul, pointAdd, G, n
from gmpy2 import f_mod, mul
from core.fieldArith import modinv

def genKeys():
    # Generates a random private key p and calculates the Public Key q.
        #Q = p * G (The starting point on the curve).
    p = secrets.randbelow(n-1) + 1  # secrets.randbelow is used for randomness which is cryptographically more secure.
    return (p, scalMul(p, G))

def sign(m: bytes, d: int):
    #  Signs a message m using a Private Key d.
    #Returns a signature (r, s).
    
# 1. k is a random number 
# If k is ever reused, the private key can be stolen  but it practically never happens 
    k = secrets.randbelow(n-1) + 1
# 2. Turn the message hash into a integer z
    z = f_mod(int.from_bytes(sha256(m).digest(), 'big'), n)

    r = scalMul(k, G)[0]  # 3. r is the x-coordinate of the point k*G
# 4. s = k⁻¹ * (z + r*d) mod n
    s = f_mod(mul(modinv(k, n), z + mul(r, d)), n)
    return (r, s)

def verify(m: bytes, sgn: tuple, Q: tuple):
    # Checks if a signature (r, s) is valid for message m using Public Key .
     # convert message hash into integer
    z = f_mod(int.from_bytes(sha256(m).digest(), 'big'), n)
    # steps to rebuild the signature point
    # u1 = z/s and u2 = r/s
    u1 = f_mod(mul(modinv(sgn[1], n), z), n)
    u2 = f_mod(mul(modinv(sgn[1], n), sgn[0]), n)
    
    # make the point again: P = u1*G + u2*Q
# if valid, x of P should be same as r
    return f_mod(pointAdd(scalMul(u1, G), scalMul(u2, Q))[0], n) == sgn[0]

def rsToDict(sgn: tuple):
    #Convert (r, s) into hex so it can be stored as JSON.
    return {'r': format(sgn[0], '064x'), 's': format(sgn[1], '064x')}

def dictToRS(d: dict):
    #Convert stored hex back to (r, s).
    return (int.from_bytes(bytes.fromhex(d['r']), 'big'), 
            int.from_bytes(bytes.fromhex(d['s']), 'big'))