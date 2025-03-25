from Present64 import Present
import itertools
import random
import math

def genList(aCount):
    valueList = []
    c = ""
    for i in range(64-aCount):
        c += str(random.randint(0,1))
    aList = list(itertools.product([0,1], repeat=aCount))
    for i in range(len(aList)):
        a = ''.join(map(str, aList[i]))
        value = c + a
        valueList.append(int(value, base=2))
    return valueList

def distinguisher(plaintextList):
    present = Present(rounds=4)
    ciphertextList = []
    for plaintext in plaintextList:
        ciphertext = present.encrypt(plaintext)
        ciphertextList.append(ciphertext)
    xorSum = 0
    for i in range(len(ciphertextList)):
        xorSum ^= ciphertextList[i]
    return xorSum

p = [0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51,
    4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55,
    8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59,
    12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63]
sbox = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
p_inverse = [p.index(i) for i in range(64)]
sbox_inverse = [sbox.index(i) for i in range(16)]

def keyRecovery(present, plaintextList, keyList):
    """
    From a set of plaintext plaintextList, filter out some wrong keys that are still in keyList
    """
    ciphertextList = []
    for plaintext in plaintextList:
        ciphertext = present.encrypt(plaintext)
        ciphertextList.append(ciphertext)

    ciphertextListPrime = []
    for ciphertext in ciphertextList:
        res = 0
        for i in range(64):
            res += ((ciphertext >> i) & 0x1) << p_inverse[i]
        ciphertextListPrime.append(res)
    
    for i in range(16):
        temp = []
        for k in keyList[i]:
            xorSum = 0
            for y in ciphertextListPrime:
                x = sbox_inverse[((y >> (i * 4)) & 0xF) ^ k]
                xorSum ^= x
            if xorSum == 0:
                temp.append(k)
        keyList[i] = temp

present = Present(rounds=5)
keyList = [list(range(16)) for _ in range (16)]

while(math.prod(len(x) for x in keyList) > (1 << 10)):
	#Generate a set of plaintexts with the proper structure 
	plaintextList = genList(4)
	keyRecovery(present, plaintextList, keyList)

plain = genList(4)[0]
candidates = list(itertools.product(*keyList))
for c in candidates:
    kPrime = 0
    for i in range(16):
        # kPrime += c[i] * 16**(i)
        kPrime |= c[i] << (4*i)
    k = 0
    for i in range(64):
        k += ((kPrime >> i) & 0x1) << p[i]

    if k == present.rk[-1]:
        print(f"k5 = {hex(k)}")

    for i in range(5,0,-1):
        k ^= i << 15
        k = (sbox_inverse[k >> 60] << 60) | (k & (2 ** 60 - 1))
        k = ((k & (2 ** 45 - 1)) << 19) | (k >> 45) 
    c1 = Present(rounds=5, key=k).encrypt(plain)
    c2 = present.encrypt(plain)
    if c1 == c2:
        print("Found key:", k)
        break

"""
We get candidates for p_inverse(k)
for each candidate (itertools.product):
	compute k from p_inverse(k) (p_inverse(k) is the candidate)
	inverse the key schedule to get the first round key (whichshould be the master key)
	So we get a candidate mk for the master key
	To check if it's correct:
		- Pick a random plaintext p
		- Encrypt p with mk -> c1
		- Encrypt p with the original oracle (present) -> c2
		if c1 == c2 :
			key is correct, print it
		  
		  
"""