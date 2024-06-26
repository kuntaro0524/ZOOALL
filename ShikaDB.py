import os
import getpass
import pysqlite2.dbapi2 as sqlite3
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

class ShikaDB:
	def __init__(self,dbfile,diffscan_log):
		self.slog=bl_logfiles.BssDiffscanLog(diffscan_log)
		self.slog.remove_overwritten_scans()
		self.dbfile=dbfile
		self.isRead=False

	def read(self):
		try:
			startt = time.time()
			self.result = []
			con = sqlite3.connect(self.dbfile, timeout=10)
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
	
			for scan in self.slog.scans:
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
					#print gonio,nspots
					self.result.append((gonio,nspots))
	
		finally:
			#print self.result
			#for a in self.result:
				#print a
        		self.isRead=True

	def getAll(self):
		if self.isRead==False:
			self.read()
		return self.result

	def getThresh(self,thresh):
		if self.isRead==False:
			self.read()
		new_list=[]
		for r in self.result:
			xyz,score=r
			if float(score) > float(thresh):
				new_list.append((xyz,score))
		return new_list

jj=ShikaDB("./asada.db","./asada.log")
good_spots=jj.getThresh(1)

for s in good_spots:
	print s
