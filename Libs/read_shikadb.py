import sqlite3, sys
import pickle

con = sqlite3.connect("shika.db", timeout=10)
c = con.execute("select filename,spots from spots")
dbspots = dict([(str(x[0]), pickle.loads(str(x[1]))) for x in c.fetchall()])
con.close()

frame_num = int(sys.argv[1])
fname = "2d_%06d.img" % frame_num
spots= dbspots[fname]["spots"]

for spot in spots:
    y,x,snr,d = spot
    print(x,y,snr)
