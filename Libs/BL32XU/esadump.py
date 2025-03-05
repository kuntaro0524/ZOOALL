import ESA,os,sys

esa = ESA.ESA("zoo.db")
#print "BEFORE"
ppp = esa.getDict()

index=1
for p in ppp:
    print "isMount",p['isMount']
    print "isLoopCenter",p['isLoopCenter']
    print "isRaster",p['isRaster']
    print "isDS",p['isDS']
    print "# crystals helical",p['nds_helical']
