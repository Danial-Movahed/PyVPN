from random import choice as c
class Encryption:
    def __init__(self) -> None:
        with open("Nenc.txt","r") as f:
            self.enc = eval(f.read())

        with open("Ndec.txt","r") as f:
            self.dec = eval(f.read())
    def encode(self,inp):
        res = "".join([c(self.enc[i]) for i in inp])
        return res
    def decode(self,inp):
        sinp = []
        for i in range(0,len(inp),7):
            sinp.append(inp[i:i+7])
        res = "".join([self.dec[i] for i in sinp])
        return res
