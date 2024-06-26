import sys
import os
import math
import tempfile
import getpass
import sqlite3
import matplotlib
matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )
import matplotlib.figure
import matplotlib.backends.backend_agg
import matplotlib.backends.backend_wxagg
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle, Ellipse
import wx
import wx.lib.newevent
import wx.lib.agw.pybusyinfo
import wx.html
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import datetime
import time
import glob
import cPickle as pickle
import collections
import threading
import subprocess
import socket
import xmlrpclib
import re
import copy
import zmq
import numpy
import scipy.spatial

dbdir="./"
dbfile = os.path.join(dbdir,"shika.db")

con = sqlite3.connect(dbfile, timeout=10)
cur = con.cursor()

con = sqlite3.connect(dbfile, timeout=10)
cur = con.cursor()

c = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='status';")
if c.fetchone() is None:
    shikalog.error("No 'status' in %s" % dbfile)

c = con.execute("select filename,spots from spots")
results = dict(map(lambda x: (str(x[0]), pickle.loads(str(x[1]))), c.fetchall()))

for r in results.values():
    print r
    if not r["spots"]: continue
    ress = numpy.array(map(lambda x: x[3], r["spots"]))
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
