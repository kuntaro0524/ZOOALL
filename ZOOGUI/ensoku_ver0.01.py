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

# Valid keys for ENSOKU
keys = esa.getKeyList()

show_list = ["p_index", "isSkip", "isDS", "puckid", "pinid",
                "mode","score_min","score_max", "maxhits","dist_ds",
                "total_osc","osc_width","cry_max_size_um", "loopsize", "isDone",
                "o_index","sample_name"]

width_list = [80, 50, 30, 80, 50,
              70, 70, 70, 25, 70,
              70, 50, 70, 70, 50,
              50, 250]

beChanged = [1, 1, 0, 0, 0, 
             1, 1, 1, 1, 1, 
             1, 1, 1, 1, 1, 
             1, 0]

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin, listmix.CheckListCtrlMixin):
    ''' TextEditMixin allows any column to be edited. '''

    # ----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)
        listmix.CheckListCtrlMixin.__init__(self)


class Repository(wx.Frame):

    def makeTableParams(self, conds):
        # Making table for showing on GUI
        line_index = 0
        contents = []
        for cond in conds:
            key_index = 0
            for key in show_list:
                contents.append((line_index, key_index, cond[key]))
                key_index += 1
            line_index += 1

        return contents

    # setting parameters to show on the GUI table
    def setValues(self, contents, isInitial=True):
        if isInitial == True:
            self.start_index = sys.maxint
            #print "START_INDEX=",self.start_index
        # If this is not the first tabling, this should delete current lines.
        else:
            n_data = self.list.GetItemCount()
            #print "n_data",n_data
            # DeleteItem deletes the 'first' line only: a code should delete a line
            for line_index in range(0, n_data):
                self.list.DeleteItem(0)

        #print "LEN=", len(contents)
        for content in contents:
            line_index, key_index, value = content
            str_value = "%s" % value
            #print "LINE,KEY,STR=",line_index, key_index, str_value
            if key_index == 0:
                self.list.InsertStringItem(line_index, str_value)
            else:
                self.list.SetStringItem(line_index, key_index, str_value)

    def setColours(self, line_index, color):
        if isSkip == 1 and isDS == 0:
            self.list.SetItemBackgroundColour(index, 'Grey')
        if isSkip == 1 and isDone == 1:
            self.list.SetItemBackgroundColour(index, 'blue')
        elif isDone == 1:
            self.list.SetItemBackgroundColour(index, 'Green')
        elif isDone > 1000:
            self.list.SetItemBackgroundColour(index, 'Orange')
        elif isSkip == 0 and isDS == 0:
            self.list.SetItemBackgroundColour(index, 'Cyan')

    def readValues(self):
        n_data = self.list.GetItemCount()
        print "N_DATA=",n_data

        contents = []
        for line_index in range(0, n_data):
            for key_index in range(0, len(show_list)):
                str_value = self.list.GetItemText(line_index, key_index)
                contents.append((line_index, key_index, str_value))
        
        """
        for content in contents:
            print content
        """

        return contents

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(1200, 400))

        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel, -1)
        rightPanel = wx.Panel(panel, -1)

        self.log = wx.TextCtrl(rightPanel, -1, style=wx.TE_MULTILINE)
        self.list = EditableListCtrl(rightPanel, 0, size=(400, 300), style=wx.LC_REPORT | wx.LC_HRULES)

        column_index = 0
        for valid_param in show_list:
            width_option = int(width_list[column_index])
            #width_option = "width=%s" % width_list[column_index] 
            self.list.InsertColumn(column_index, valid_param, width=width_option)
            column_index += 1

        #self.list.InsertColumn(0, 'PriorityIndex', width=80)

        contents = self.makeTableParams(conds)

        line_index = 0
        #contents.append((line_index, key_index, cond[key]))

        self.setValues(contents)

        vbox2 = wx.BoxSizer(wx.VERTICAL)

        sel = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
        des = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))
        apply = wx.Button(leftPanel, -1, 'Apply', size=(100, -1))
        setskip = wx.Button(leftPanel, -1, 'set SKIP', size=(100, -1))
        unsetskip = wx.Button(leftPanel, -1, 'unset SKIP', size=(100, -1))
        updateButton = wx.Button(leftPanel, -1, 'Update', size=(100, -1))

        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=sel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=des.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=apply.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushSkip, id=setskip.GetId())
        self.Bind(wx.EVT_BUTTON, self.UnsetSkip, id=unsetskip.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushUpdate, id=updateButton.GetId())

        vbox2.Add(sel, 0, wx.TOP, 5)
        vbox2.Add(des)
        vbox2.Add(apply)
        vbox2.Add(setskip)
        vbox2.Add(unsetskip)
        vbox2.Add(updateButton)

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        vbox.Add(self.log, 0.5, wx.EXPAND)
        vbox.Add((-1, 10))

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))

        panel.SetSizer(hbox)

        self.Centre()
        self.Show(True)

    def PushUpdate(self, event):
        conds = esa.getSortedDict()
        num = self.list.GetItemCount()

        packages = []
        gui_index = 0
        index_list = []

        contents = self.makeTableParams(conds)
        self.setValues(contents,isInitial = False)
        print "updated."

    def readCurrentSkipList(self):
        num = self.list.GetItemCount()
        for n_column in range(num):
            # isSkip
            print "Reading"
            print self.list.GetItemText(n_column, 1)

    def OnSelectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i)

    def OnDeselectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)

    def getKeyIndex(self, param_name):
        key_index = 0
        for key in keys:
            if key == param_name:
                return key_index
            else:
                key_index += 1
        return -9999

    def PushSkip(self, event):
        num = self.list.GetItemCount()
        for line_index in range(num):
            if self.list.IsChecked(line_index):
                self.list.SetStringItem(line_index, 1, "1")
                # original index
                o_index = int(self.list.GetItemText(line_index, 15))
                print "O_INDEX= %5d is skipped" % o_index
                esa.updateValueAt(o_index, "isSkip", 1)
                self.list.SetItemBackgroundColour(line_index, 'Grey')

    # CHIKARATSUKITE BETAGAKI
    # show_list = ["p_index", "isSkip", 
    #           "mode","score_min","score_max", "maxhits","dist_ds",
    #           "total_osc","osc_width","cry_max_size_um", "loopsize", "isDone",
    def getPinData(self, contents, line_index, mod_param_index):
        pin_data = []
        work_idx = 0
        for content in contents:
            line_index, key_index, str_value = content
            if work_idx == line_index:
                print work_idx
                for check_idx in mod_param_index:
                    print check_idx
                    if key_index == check_idx:
                        if show_list[key_index] == "o_index":
                            o_index = int(str_value)
                        elif show_list[key_index] == "p_index":
                            p_index = int(str_value)
                        elif show_list[key_index] == "isSkip":
                            isSkip = int(str_value)
                        elif show_list[key_index] == "mode":
                            mode = str_value
                        elif show_list[key_index] == "score_min":
                            score_min = float(str_value)
                        elif show_list[key_index] == "score_max":
                            score_max = float(str_value)
                        elif show_list[key_index] == "maxhits":
                            maxhits = int(str_value)
                        elif show_list[key_index] == "dist_ds":
                            dist_ds = float(str_value)
                        elif show_list[key_index] == "total_osc":
                            total_osc = float(str_value)
                        elif show_list[key_index] == "osc_width":
                            osc_width = float(str_value)
                        elif show_list[key_index] == "cry_max_size_um":
                            cry_max_size_um = float(str_value)
                        elif show_list[key_index] == "loopsize":
                            loopsize = float(str_value)
                        elif show_list[key_index] == "isDone":
                            isDone = int(str_value)
            work_idx += 1
        return o_index,p_index,isSkip,mode,score_min,score_max,maxhits,dist_ds,total_osc,osc_width,cry_max_size_um,loopsize,isDone

    def OnApply(self, event):
        #logger.info("Event!!")
        n_data = self.list.GetItemCount()

        packages = []
        gui_index = 0
        index_list = []

        line_index = 0
        contents = self.readValues()
        #contents.append((line_index, key_index, str_value))

        mod_param_index = []
        for cindex in range(0,len(beChanged)):
            if beChanged[cindex] == 0:
                continue
            else:
                print "VALID=",show_list[cindex]
                mod_param_index.append(cindex)
        print "HEREERERE",mod_param_index

        for work_index in range(0, n_data):
            print "WORK_INDEX=",work_index
            #print contents
            print mod_param_index
            o_index,p_index,isSkip,mode,score_min,score_max,maxhits,dist_ds,total_osc,osc_width,cry_max_size_um,loopsize,isDone = \
                self.getPinData(contents, work_index, mod_param_index)
            esa.updateValueAt(o_index, "isSkip", isSkip)
            esa.updateValueAt(o_index, "p_index", p_index)
            esa.updateValueAt(o_index, "score_min", score_min)
            esa.updateValueAt(o_index, "score_max", score_max)
            esa.updateValueAt(o_index, "maxhits", max_hits)
            esa.updateValueAt(o_index, "cry_min_size_um", cry_min_size)
            esa.updateValueAt(o_index, "cry_max_size_um", cry_max_size)
            esa.updateValueAt(o_index, "loopsize", loop_size)

        self.PushUpdate(event)

    def UnsetSkip(self, event):
        num = self.list.GetItemCount()
        for line_index in range(num):
            if line_index == 0:
                self.log.Clear()
            if self.list.IsChecked(line_index):
                isSkip = 0
                ichar = "%s" % isSkip
                self.list.SetStringItem(line_index, 1, ichar)
                o_index = int(self.list.GetItemText(line_index, 15))
                esa.updateValueAt(o_index, "isSkip", isSkip)
                self.list.SetItemBackgroundColour(line_index, 'CYAN')

app = wx.App()
Repository(None, -1, 'ENSOKU')
app.MainLoop()
