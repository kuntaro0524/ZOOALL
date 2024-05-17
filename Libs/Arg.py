import argparse    

parser = argparse.ArgumentParser(description='getget')

#parser.add_argument('arg1', help='arg1 explanation')
#parser.add_argument('arg2', help='foooo')
parser.add_argument('--csv',help='1st CSV file') 
parser.add_argument('--csv2', help='2nd CSV file')
parser.add_argument('--csv3', help='3rd CSV file')
parser.add_argument('--dbfile', help='definition of the database file')

args = parser.parse_args()   

csvlist = []
csv_flag = False

if args.csv != None:
    csv_flag = True
    csv_name = args.csv
    csvlist.append(csv_name)

if args.csv2 != None:
    csv2_name = args.csv2
    csvlist.append(csv2_name)

if args.csv3 != None:
    csv3_name = args.csv3
    csvlist.append(csv3_name)

if csv_flag == True:
    for csvfile in csvlist:
        print(csvfile)
else:
    print("DBFILE=", args.dbfile)
