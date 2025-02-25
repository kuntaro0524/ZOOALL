import sys

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

import Date

datestr = Date.Date().getNowMyFormat(option="date")

csv_file = open("%s_test.csv" % datestr, "w")

for i in range(1,1000):
    csv_file.write("/isilon/users/admin45/admin45/%s_ZOOtest/%02d/,1,helical,1,5,TEST,1,20,20,10,10,0.02,180,200,10,300,1,360,0.1,20,20,0.02,250,10,0,1,1,PE7-0192626-bs-01,20,20,40,60,0,0,0,0,0,0,0,0,0,none,none,none,none,none,none,none,none,none,none,none,none\n"%(datestr, i))
