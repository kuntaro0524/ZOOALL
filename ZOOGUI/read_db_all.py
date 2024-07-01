#!/usr/bin/python
import wx
import sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import wx.lib.mixins.listctrl as listmix
#import logger, logger.config

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

import ESA

esa = ESA.ESA(sys.argv[1])
esa.listDB()
conds = esa.getSortedDict()

keys = esa.getKeyList()
li=[]
valid_list = ["p_index", "isSkip", "isDS", "puckid", "pinid","mode","score_min","score_max",
                "maxhits","dist_ds","total_osc","osc_width","cry_max_size_um","loopsize","isDone","o_index","sample_name"]

def isValid(key):
    for valid_key in valid_list:
        if key == valid_key:
            return 1
    return 0

# Making valid list
valid_indices=[]
for key in keys:
    valid_indices.append(isValid(key))

# Making table for showing on GUI
line_index = 0
contents = []
for cond in conds:
    key_index = 0
    for key in valid_list:
        contents.append((line_index, key_index, cond[key]))
        key_index += 1
    line_index += 1
#display_list 

for content in contents:
    print "########################"
    print content
