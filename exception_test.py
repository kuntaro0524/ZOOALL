import sys,os
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import MyException

class something1():
    def __init__(self):
        self.something1=5
        self.some2=something2()

    def anaana(self):
        try:
            answer=self.some2.getAdd(self.something1)
        except:
            print "REIGAI in something2"
            answer=0
        finally:
            return answer

class something2():
    def __init__(self):
        self.something2=10
    
    def getAdd(self, value):
        try:
            answer = value + self.something2/0.0
        except:
            raise MyException.MyException("HEBI.mainLoop : Vertical scan could not find crystals.")
        finally:
            print "something2",answer
            return answer

if __name__ == "__main__":
    s1=something1()
    print s1.anaana()
