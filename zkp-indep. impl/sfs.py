from core.ec import G,n,xyTob64,xyFromb64
from core.ecdsa import scalMul,pointAdd
from hashlib import sha256
from gmpy2 import f_mod,mul
import secrets

def zkpProof(priv_k:int,m:bytes):
    r=secrets.randbelow(n-1)+1
    R=scalMul(r,G)
    Y=scalMul(priv_k,G)
    c=int.from_bytes(sha256(str(R)+str(Y)+m.hex()).digest(),'big')
    s=f_mod(r+mul(c,priv_k),n)
    return {
        'R':xyTob64(R),
        's':format(s,'064x'),
        'Y':xyTob64(Y)
    }

def zkpVerify(pf:dict,m:bytes):
    R=xyFromb64(pf['R'])
    Y=xyFromb64(pf['Y'])
    c=int.from_bytes(sha256(str(R)+str(Y)+m.hex()).digest(),'big')
    s=int.from_bytes(bytes.fromhex(pf['s']),'big')
    return pointAdd(R,scalMul(c,Y))==scalMul(s,G)