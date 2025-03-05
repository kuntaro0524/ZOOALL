import Zoo, sys,os,csv
if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    puck_list=zoo.getSampleInformation()

<<<<<<< HEAD
    print(puck_list)

    csvfile = sys.argv[1]
    n_ng = 0
    with open(csvfile, 'r') as f:
=======
    print puck_list

    csvfile = sys.argv[1]
    n_ng = 0
    with open(csvfile, 'rb') as f:
>>>>>>> zoo45xu/main
        b = csv.reader(f)
        header = next(b)
        # CSV line processing
        for t in b:
            puckid, pinid = t[3],t[4]
            found_flag = False
            for puck_info in puck_list:
                if puck_info == puckid:
                    found_flag = True
                    break
            #print "KOKONIKURUKA"
            if found_flag == False:
<<<<<<< HEAD
                print("NG,",puckid,pinid) 
                n_ng += 1

print("NG number = ", n_ng)
=======
                print "NG,",puckid,pinid 
                n_ng += 1

    zoo.disconnect()
print "NG number = ", n_ng
>>>>>>> zoo45xu/main
