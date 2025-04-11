import sys
import os
import math
import tempfile
import getpass
import sqlite3
import datetime
import time
import glob
import pickle as pickle
import collections
import threading
import subprocess
import socket
import xmlrpc.client
import re
import copy
import numpy

dbdir="./"
time1=datetime.datetime.now()
print("start            ",time1)
dbfile = os.path.join(dbdir,"shika.db")

time1=datetime.datetime.now()
print("dbfile join      ",time1)

con = sqlite3.connect(dbfile, timeout=10)

time1=datetime.datetime.now()
print("finished: connect",time1)
cur = con.cursor()

c = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='status';")
time1=datetime.datetime.now()
print("finished: execute",time1)

if c.fetchone() is None:
    shikalog.error("No 'status' in %s" % dbfile)

time1=datetime.datetime.now()
print("finished: clone  ",time1)

c = con.execute("select filename,spots from spots")
results = dict([(str(x[0]), pickle.loads(str(x[1]))) for x in c.fetchall()])

time1=datetime.datetime.now()
print("finished: results get",time1)

for r in list(results.values()):
    #print r
    if not r["spots"]: continue
    ress = numpy.array([x[3] for x in r["spots"]])
    test = numpy.zeros(len(r["spots"])).astype(numpy.bool)
    for i in reversed(numpy.where(test)[0]): del r["spots"][i]


"""
for imgf, (gonio, gc) in scan./ilename_coords:
    stat = Stat()
    if imgf not in results: continue
    snrlist = map(lambda x: x[2], results[imgf]["spots"])
    stat.stats = (len(snrlist), sum(snrlist), numpy.median(snrlist) if snrlist else 0)
    stat.spots = results[imgf]["spots"]
    stat.gonio = gonio
    stat.grid_coord = gc
    stat.scan_info = scan
    stat.thumb_posmag = results[imgf]["thumb_posmag"]
    stat.params = results[imgf]["params"]
    stat.img_file = os.path.join(self.ctrlFrame.current_target_dir, imgf)
    result.append((stat.img_file, stat))
"""
