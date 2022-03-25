import datetime as dt

a = (10 + 20.50) * ((30 ** 2) - 12)
a, b = 10, 20
c = "Subscript"[2:4]
b = "Hello ".capitalize() + "World ! " + ("test" + ") heunthoe"[2::] + str("ste" + "<3"))
d = [1,4,2,7,5,8,6][:4]
e = (8,5,5,9,0,5,54,8,98,6)[1::2]
f = {"K1": ("1}23"), "K2": 40, "K3": True}
g = [True, False, None]
h = ~True or True
i = {1, 2,3,4 ,5}

# ASSIGN
import random
a =  int(random.randint(1, 20))
a |= int(random.randint(1, 20))
a &= int(random.randint(1, 20))
a ^= int(random.randint(1, 20))
a >>= int(random.randint(1, 20))
a <<= int(random.randint(1, 20))
a += int(random.randint(1, 20))
a -= int(random.randint(1, 20))
a *= int(random.randint(1, 20))
a /= int(random.randint(1, 20))
a %= int(random.randint(1, 20))
a //= int(random.randint(1, 20))
a **= int(random.randint(1, 20))

# OpMath
a = int(5 + 7 ** 2) + int(3 - 2) % int(5 * 6) // int(10 / 2)
b = ~ 10 << 2 | 20 >> 3 & 23 ^ 8
c = not a

# Compare
d = a == b and a != b or a > b and a < b
e = a >= b or a <= b and a is b or a is not b

# FOR
for (i, j) in zip(range(1), range(1)) :
    print(i, j)
    print(i, j)
    print(i, j)
    print(i, j)
    for ah in range(1) :
        print(ah)
        for ahhh in range(1) :
            print("test test")
            for (i, j) in zip(range(1), range(1)) :
                print(i, j)
                print(i, j)
                print(i, j)
                print(i, j)
                for ah in range(1) :
                    print(ah)
                    for ahhh in range(1) :
                        print(ahhh)

# IF
a = 10
b = 20
c = a > 0 and b == 20
if a > 0 and (b == 20 and c):
    print("INSIDE")
    if a == 20 :
        print("Not 20")
        if a == 30 :
            print("Not 30")
    elif b == 1 :
        print("Nothing")
    else: 
        print(a)
else :
    print("LOWWW")