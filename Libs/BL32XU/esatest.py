import ESA,os,sys

esa = ESA.ESA("zoo.db")
esa.makeTable("zoo.db", sys.argv[1],False)

esa.listDB()
#print "BEFORE"
ppp = esa.getDict()

for p in ppp:
    print p['isSkip']

print "BEFORE",esa.isSkipped(1)
print "BEFORE",esa.isSkipped(2)
print "CURRENT"

esa.incrementInt(1,"isSkip")
esa.incrementInt(2,"isSkip")

print "AFTER", esa.isSkipped(1)
print "AFTER", esa.isSkipped(2)
