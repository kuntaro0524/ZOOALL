import csv,sys

csvfile=sys.argv[1]

with open(csvfile,'rb') as f:
    b = csv.reader(f)
    header = next(b)
    for t in b:
        print t
