import os, math, sys, numpy

class LogString:

    def __init__(self):
        self.isStart = False

    def knowTypeOfObjects(self, objects):
        print type(objects)
        if type(objects) == 'tuple':
            print "DDDDDDDDDDDDDDDDDDDDDDDDDD"

    def list2str(self, str_list):
        rtn_str = ""
        for obj in str_list:
            rtn_str += "%s " % obj
        return rtn_str

    def floatArray2str(self, array, comment, isReturn=False):
        if isReturn == False:
            rtn_str = "%s " % comment
        else:
            rtn_str = ""
        for component_i in array:
            if isReturn == True:
                rtn_str += "%s %8.5f\n" % (comment, component_i)
            else:
                rtn_str += "%8.5f " % component_i
        return rtn_str

    def intArray2str(self, array, comment, isReturn=False):
        if isReturn == False:
            rtn_str = "%s " % comment
        else:
            rtn_str = ""
        for component_i in array:
            if isReturn == True:
                rtn_str += "%s %5d\n" % (comment, component_i)
            else:
                rtn_str += "%5d " % component_i
        return rtn_str


if __name__ == "__main__":

    ls = LogString()

    params = ('test', 'test2', 'test3')
    ls.knowTypeOfObjects(params)
    print ls.list2str(params)

    dimension = [35, 55]
    print ls.intArray2str(dimension)