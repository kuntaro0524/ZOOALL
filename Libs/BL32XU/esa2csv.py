import ESA,os,sys

esa = ESA.ESA("zoo.db")
esa.makeTable("zoo.db", sys.argv[1],False)
#esa.listDB()
esa.save_csv("zoo_new.csv")
