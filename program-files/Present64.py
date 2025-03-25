import random

class Present:
    def __init__(self, rounds=31, key=-1):
        if key == -1:
            key = random.randrange(1 << 64)

        self.rk = genRoundKeys(key, rounds)
        self.rounds = rounds

    def encrypt(self, x):
        for i in range(self.rounds):
            x = addRoundKey(x, self.rk[i])
            x = sBoxLayer(x)
            x = pLayer(x)
        x = addRoundKey(x, self.rk[self.rounds])
        return x

sbox = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
p = [0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51,
    4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55,
    8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59,
    12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63]

def genRoundKeys(key, rounds):
    rk = []
    for i in range(rounds+1):
        rk.append(key)
        key = ((key & (2 ** 19 - 1)) << 45) + (key >> 19)
        key = (sbox[key >> 60] << 60) + (key & (2 ** 60 - 1))
        key ^= (i+1) << 15
    return rk

def addRoundKey(x, rk):
    return x ^ rk

def sBoxLayer(x):
    res = 0
    for i in range(16):
        res += (sbox[(x >> (i * 4)) & 0xF]) << (i * 4)
    return res

def pLayer(x):
    res = 0
    for i in range(64):
        res += ((x >> i) & 0x1) << p[i]
    return res

if __name__ == "__main__":
    present = Present(rounds=5)
    plain = 0
    res = hex(present.encrypt(plain))
    print(res)