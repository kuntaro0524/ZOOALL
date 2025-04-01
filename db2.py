import os
import getpass
import sqlite3
import time
import cPickle as pickle
import numpy

from yamtbx.dataproc import bl_logfiles

def add_results(results):
    for f, stat in results: current_stats[f] = stat

class Stat:
    def __init__(self):
        self.img_file = None
        self.stats = [] # n_spots, total, mean
        self.spots = []
        self.gonio = None
        self.grid_coord = None
        self.scan_info = None
        self.params = None
        self.thumb_posmag = None
        self.detector = ""

def load_results(dbfile,diffscan_log):
    slog = bl_logfiles.BssDiffscanLog(diffscan_log)
    slog.remove_overwritten_scans()

    try:
        startt = time.time()
        result = []
        con = sqlite3.connect(dbfile, timeout=10)
        cur = con.cursor()

        c = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='status';")
        if c.fetchone() is None:
	    print "c.fetchone failed"
            return

        c = con.execute("select filename,spots from spots")
        results = dict(map(lambda x: (str(x[0]), pickle.loads(str(x[1]))), c.fetchall()))

        for r in results.values():
            if not r["spots"]: continue
            ress = numpy.array(map(lambda x: x[3], r["spots"]))
            test = numpy.zeros(len(r["spots"])).astype(numpy.bool)
            #for rr in exranges: test |= ((min(rr) <= ress) & (ress <= max(rr)))
            for i in reversed(numpy.where(test)[0]): del r["spots"][i]

        for scan in slog.scans:
            for imgf, (gonio, gc) in scan.filename_coords:
                stat = Stat()
                if imgf not in results: continue
		#print "IMGF=",imgf
		nspots=len(results[imgf]["spots"])
                snrlist = map(lambda x: x[2], results[imgf]["spots"])
		#print "RESULTS:",imgf,nspots,len(snrlist)

		""" KEITARO ORIGINAL
                stat.stats = (len(snrlist), sum(snrlist), numpy.median(snrlist) if snrlist else 0)
                stat.spots = results[imgf]["spots"]
                stat.gonio = gonio
                stat.grid_coord = gc
                stat.scan_info = scan
                stat.thumb_posmag = results[imgf]["thumb_posmag"]
                stat.params = results[imgf]["params"]
		"""
		x,y,z=gonio
		print x,y,z,nspots
                result.append((stat.img_file, stat))

    finally:
        d=None

load_results("./asada.db","./asada.log")
