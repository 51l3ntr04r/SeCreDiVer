from secrets import randbelow
from gmpy2 import powmod

def modinv(a: int, p: int):
    #In a modular field, you can not just divide two numbers .
    #To divide by a number, you multiply by its modular inverse.
    # Using Fermat's Little Theorem for calculating modular inverse of a = (a^(p-2) % p).       """
    # This works because for a prime p, a^(p-1) is congruent to 1 (mod p).
    # Therefore, a * a^(p-2) is congruent to 1 (mod p).
    return powmod(a, p - 2, p)  #(a^(p-2) % p)  % - modulus

# we have not used this function in our project but if we want to scale our project in future then we can use this test. Instead 
# of this we have used an standard prime number which is mostly used worldwide as a standard
def is_prime(m: int, k=20):
    """ The Miller-Rabin primality Test:
    it is a fast way to check if a big number is prime or not.
    We run k number of tests.
    """
    if m < 2: return False
    elif m == 2: return True
    
    #  convert (m-1) into (2^e * q)
    # We take out all the factors of 2 from (m-1).
    e, q = 0, m - 1
    while((q & 1) == 0):
        q //= 2
        e += 1
        
    #  Start the Tests
    for i in range(k):
        # Pick a random number r to test for prime number
        r = randbelow(m - 3) + 2
        p = q
        # 3. Square and Multiply logic
        while(p < m - 1):
            # If r^q % m is 1 or (m-1), the number m passes this round.
            if p == q and (powmod(r, p, m) == 1 or powmod(r, p, m) == m - 1):
                break
            # If the square  becomes (m-1), it passes.
            elif powmod(r, p, m) == m - 1:
                break
            else:
                p *= 2 # Keep squaring the exponent
        
        # If we reached the end without a pass, the number is composite.
        if p == m - 1:
            return False
            
    # If it passes all k tests, it is probably prime.
    return True