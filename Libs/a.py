import sys,os
import BLFactory


class Test:
    def __init__(self, gonio):
        self.gonio = gonio

    def pppGonio(self):
        return self.gonio.getXYZmm()

if __name__=="__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()
    gonio = blf.getGoniometer()
    test = Test(gonio)
    print(test.pppGonio())