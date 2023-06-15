from random import choice as c
import string as s

chars = [chr(i) for i in range(127)]
chars_2 = [chr(i)*10 for i in range(127)]
charsflat = [i for t in chars_2 for i in t]
a = [i for i in s.ascii_letters+s.digits+s.punctuation]
encoded = [list(set([c(a)+c(a)+c(a)+c(a)+c(a)+c(a)+c(a) for _ in range(20)]))[:10] for _ in range(200)]
enc = set(map(tuple,encoded))
encoded = list(map(list,enc))[:127]

seen = set()
repeated = set()
for l in encoded:
    for i in set(l):
        if i in seen:
            repeated.add(i)
        else:
            seen.add(i)
dups = repeated == set()
if not dups: print("Duplicates found, run code again!"); exit()

print(dict(zip(chars,encoded)))
print ()
encflat = [i for t in encoded for i in t]
print(dict(zip(encflat,charsflat)))
