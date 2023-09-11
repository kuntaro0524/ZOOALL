import MyException

class Hoge:
    def __init__(self,value):
        self.value = value
        try:
            hogeko = Hogeko(value)
        except MyException.NandaKandaExcept as e:
            raise e
            #raise MyException.NandaKandaExcept(e.args)

class Hogeko:
    def __init__(self, value):
        raise MyException.NandaKandaExcept("Hogeko no naka kara yobaremashita")

while True:
    try:
        selection = int(eval(input("What?")))
        if selection ==1:
            tmp = int('foo')
    
        elif selection == 2:
            tmp = 'tmp'[5]
    
        elif selection == 3:
            print("")
            print("No exception")
    
        elif selection == 4:
            print("End!!")
            break

        elif selection == 5:
            raise MyException.MyException("Nante kottai konoyarou")

        elif selection == 6:
            raise MyException.MyException("Koremata doushita kusoyarou")
    
        elif selection == 7:
            raise MyException.NandaKandaExcept("NandaKandaExcep: Original exception using Exception1",3,6,9)

        elif selection == 8:
            raise Exception("Original exception using Exception2")

        elif selection == 9:
            hoge = Hoge(1.0)
    
        else:
            print(undefined_var)

    except ValueError as e:
        print("Value error")
        print(e.args)
        print("")

    except IndexError:
        print("Index error")

    except MyException.MyException as e:
        print("Kuntaro defined exception")
        print("kuntaro defined exception args=",e.args)

    except MyException.NandaKandaExcept as e:
        print("nanda defined exception")
        print("kanda defined exception args=",e.args)

    except Exception as e:
        print("Some exception")
        print("args=",e.args)

    print("after trying")

print("Mugen loop out")
