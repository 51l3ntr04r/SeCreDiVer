from core.hashing import hash_leaf, hash_node
from core.fieldEnc import encode_field

def mkTree(fp: list[tuple[str, any]]):
    # Starts with raw data, hashes it into leaves, and pairs them up 
    #until we reach a single Merkle Root.  
    tree = list()
    tree.append([])
    
    # 1. Creating the base of merkle tree made of Leaves
    # We take every field (Name, GPA, etc.), encode it, and hash it.
    for i in range(len(fp)):
        tree[0].append(hash_leaf(encode_field(fp[i][0], fp[i][1])))
    
    # 2. pairing the hashes and making layers of nodes until we
    #    reach the merkle root layer 
    while len(tree[-1]) != 1:
        temp = list()
        for i in range(0, len(tree[-1]), 2):
            # If there is a pair, hash them together.
            if i != len(tree[-1]) - 1:
                temp.append(hash_node(tree[-1][i], tree[-1][i+1]))
            # If the last hash reamins without pair so we hashes it with itself to maintain the structure.
            else:
                temp.append(hash_node(tree[-1][i], tree[-1][i]))
        tree.append(temp)
    return tree  
#   the tree looks like this   tree = [Level_0, Level_1, Level_2]  level 0 for leaves and other levels are nodes till final merkle root
#   tree  = [["0x1a2b...", "0x3c4d...", "0x5e6f...", "0x7g8h..."],["0x9876...", "0x5432..."], ["0xABCD..."] ]

def getRoot(l: list[list[bytes]]):
    """Returns the merkle root of the tree."""
    return l[-1][0]

def getProof(l: list[list[bytes]], ind: int):
    """   used for selective disclosure feature
    Instead of showing the whole tree, we only give the adjacent hashes needed to re-calculate the root from a specific leaf 
    and check if the given field(data like age)is valid without seeing field like religion on degree.          """
    
    pftree = list()
    for i in range(len(l) - 1):
        temp = tuple()
        # If the index is even, the sibling is on the right.
        if (ind & 1) == 0:  # for checking even
            temp = (l[i][ind+1 if ind+1 < len(l[i]) else ind], 'right')
        # If the index is odd, the sibling is on the left.
        else:
            temp = (l[i][ind-1], 'left')
        pftree.append(temp)
        ind //= 2 # Move up to the next level of the tree.
    return pftree

def verifyProof(n: str, v: any, pf: list[tuple[bytes, str]], r):
    """  Takes one piece of data and its map (proof). If it build the merkle root identical to the given one then
     the diclosed data is verified """

    h = hash_leaf(encode_field(n, v)) # Hash the data provided.
    for i in range(len(pf)):
        # Combine the current hash with the sibling in the correct order.
        if(pf[i][1] == 'left'):
            h = hash_node(pf[i][0], h)
        else:
            h = hash_node(h, pf[i][0])
    # compare the calculated root with the given one if it matches then the given value of age is verified
    return h == r

def bytToStr(tb: list[list[bytes]]):
    """Converts raw binary hashes into hex strings so we can save them in a JSON file."""
    ts = list()
    for i in range(len(tb)):
        temp = [j.hex() for j in tb[i]]
        ts.append(temp)
    return ts

def strToByt(ts: list[list[str]]):
    """Converts hex strings back into raw bytes so we can do math with them again."""
    tb = list()
    for i in range(len(ts)):
        temp = [bytes.fromhex(j) for j in ts[i]]
        tb.append(temp)
    return tb