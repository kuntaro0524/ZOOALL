#!/usr/bin/python
import wx
import sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import wx.lib.mixins.listctrl as listmix
#import logger, logger.config

# Version 3.22 2019/10/25 : 
beamline = "BL32XU"

sys.path.append("/isilon/%s/BLsoft/PPPP/10.Zoo/Libs" % beamline.upper())

import ESA
<<<<<<< HEAD
import DBinfo

dbfile = sys.argv[1]
esa = ESA.ESA(dbfile)
=======

esa = ESA.ESA(sys.argv[1])
>>>>>>> zoo45xu/main
esa.listDB()
ppp = esa.getSortedDict()

packages = []
gui_index = 0
index_list = []
# 1.          p_index int,
# 2.          mode char,
# 3.          puckid char,
# 4.          pinid int,
# 5.          score_min float, 
# 6.          score_max float,
# 7.          maxhits int,
# 8.          dist_ds float,
# 9.          cry_min_size_um float,
# 10.          cry_max_size_um float,
# 11.          isSkip int,
# 12.          n_mount int,
# 13.          loopsize char,

for p in ppp:
    ttt = (p['p_index'], p['isSkip'], p['isDS'], p['puckid'], p['pinid'], p['mode'],
           p['score_min'], p['score_max'], p['maxhits'], p['dist_ds'],
           p['cry_min_size_um'], p['cry_max_size_um'], p['loopsize'], p['n_mount'], p['isDone'], p['o_index'])
    index_list.append((p['p_index'], gui_index))
    print ttt
    packages.append(ttt)
    gui_index += 1


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

    def setValues(self, index, param_list, isInitial=True):
        p_index, isSkip, isDS, puckid, pinid, mode, score_min, \
        score_max, maxhits, dist_ds, cry_min_size_um, cry_max_size_um, loopsize, n_mount, isDone, o_index = param_list

        # Priority index
        ichar = "%s" % p_index

        if isInitial == True:
            self.start_index = sys.maxint
            #print "START_INDEX=",self.start_index
        else:
            self.list.DeleteItem(index)

        #print "INDEX=",index
        #index = self.list.InsertStringItem(self.start_index, ichar)
        index = self.list.InsertStringItem(index, ichar)

        # o_index
        ichar = "%s" % o_index
        self.list.SetStringItem(index, 1, ichar)

        # isSkip
        ichar = "%s" % isSkip
        self.list.SetStringItem(index, 2, ichar)

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

        ichar = "%s" % isDS
        self.list.SetStringItem(index, 3, ichar)
        # puckID
        self.list.SetStringItem(index, 4, puckid)
        # pinID
        ichar = "%s" % pinid
        self.list.SetStringItem(index, 5, ichar)
        # Scheme
        self.list.SetStringItem(index, 6, mode)
        # score_min
        ichar = "%s" % int(score_min)
        self.list.SetStringItem(index, 7, ichar)
        # score_max
        ichar = "%s" % int(score_max)
        self.list.SetStringItem(index, 8, ichar)
        # max hit
        ichar = "%s" % maxhits
        self.list.SetStringItem(index, 9, ichar)
        # dist for data collection
        ichar = "%s" % dist_ds
        self.list.SetStringItem(index, 10, ichar)
        # min cry size
        ichar = "%s" % cry_min_size_um
        self.list.SetStringItem(index, 11, ichar)
        # max cry size
        ichar = "%s" % cry_max_size_um
        self.list.SetStringItem(index, 12, ichar)
        # Loop size
        loop_char = "%5.1f" % loopsize
        self.list.SetStringItem(index, 13, loop_char)
        # nMount
        ichar = "%s" % n_mount
        self.list.SetStringItem(index, 14, ichar)
        # isDone
        ichar = "%s" % isDone
        self.list.SetStringItem(index, 15, ichar)

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(1200, 400))

        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel, -1)
        rightPanel = wx.Panel(panel, -1)

        self.command_window = wx.TextCtrl(rightPanel, -1, 'Commandline here', size = (1000,-1), style=wx.TE_MULTILINE)
<<<<<<< HEAD
        self.sss = wx.Button(rightPanel, -1, '!!Change!!', size=(100, -1))
=======
        self.sss = wx.Button(rightPanel, -1, 'SSS button', size=(100, -1))
>>>>>>> zoo45xu/main
        self.Bind(wx.EVT_BUTTON, self.pushChangeAllButton, id=self.sss.GetId())
        self.log_window = wx.TextCtrl(rightPanel, -1, 'Commandline here', size = (1000,-1), style=wx.TE_MULTILINE)
        #self.Bind(wx.EVT_BUTTON, self.pushQQQ, id=self.qqq.GetId())

        self.list = EditableListCtrl(rightPanel, 0, size=(300, 100), style=wx.LC_REPORT | wx.LC_HRULES)
        self.list.InsertColumn(0, 'PriorityIndex', width=80)
        self.list.InsertColumn(1, 'OriginalIndex', width=80)
        self.list.InsertColumn(2, 'isSkip', width=50)
        self.list.InsertColumn(3, 'isDS', width=50)
        self.list.InsertColumn(4, 'puckID')
        self.list.InsertColumn(5, 'pinID')
        self.list.InsertColumn(6, 'Scheme')
        self.list.InsertColumn(7, 'MinScore')
        self.list.InsertColumn(8, 'MaxScore')
        self.list.InsertColumn(9, 'MaxHit')
        self.list.InsertColumn(10, 'DistDS')
        self.list.InsertColumn(11, 'CryMinSize')
        self.list.InsertColumn(12, 'CryMaxSize')
        self.list.InsertColumn(13, 'LoopSize')
        self.list.InsertColumn(14, 'n_mount')
        self.list.InsertColumn(15, 'isDone')

        # ttt=(p['p_index'],p['isSkip'],p['puckid'],p['pinid'],p['mode'],
        #     p['score_max'],p['score_max'],p['maxhits'],p['dist_ds'],p['cry_min_size_um'],
        #     p['cry_max_size_um'],p['loopsize'],p['n_mount'])

        line_index = 0
        for i in packages:
            p_index, isSkip, isDS, puckid, pinid, mode, score_min, \
            score_max, maxhits, dist_ds, cry_min_size_um, cry_max_size_um, loopsize, n_mount, isDone, o_index = i
            self.setValues(line_index, i)
            line_index += 1

        vbox2 = wx.BoxSizer(wx.VERTICAL)

        sel = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
        des = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))
        apply = wx.Button(leftPanel, -1, 'Apply', size=(100, -1))
        setskip = wx.Button(leftPanel, -1, 'set SKIP', size=(100, -1))
        unsetskip = wx.Button(leftPanel, -1, 'unset SKIP', size=(100, -1))
        updateButton = wx.Button(leftPanel, -1, 'Update', size=(100, -1))
        startModButton = wx.Button(leftPanel, -1, 'ModParams', size=(100, -1))

        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=sel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=des.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=apply.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushSkip, id=setskip.GetId())
        self.Bind(wx.EVT_BUTTON, self.UnsetSkip, id=unsetskip.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushUpdate, id=updateButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushStartMod, id=startModButton.GetId())

        vbox2.Add(sel, 0, wx.TOP, 5)
        vbox2.Add(des)
        vbox2.Add(apply)
        vbox2.Add(setskip)
        vbox2.Add(unsetskip)
        vbox2.Add(updateButton)
        vbox2.Add(startModButton)

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        vbox.Add(self.command_window)
        vbox.Add(self.sss)
        vbox.Add(self.log_window)

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))

        panel.SetSizer(hbox)

        self.Centre()
        self.Show(True)

    def pushChangeAllButton(self, event):
        command = self.command_window.GetValue()

<<<<<<< HEAD
        print "########### push change all button #########"
=======
>>>>>>> zoo45xu/main
        cols = command.split()
        if len(cols) >= 2:
            param_name = cols[0]
            param_value = cols[1]
            print "PARAm=", param_name
            print "value=", param_value

        # Get selected items
        num = self.list.GetItemCount()
        for line_index in range(num):
            n_checked = 0
            if self.list.IsChecked(line_index):
                o_index = int(self.list.GetItemText(line_index, 1))
<<<<<<< HEAD
                print "Modifying O_INDEX= %5d Param=%s Value is changed to [%s] (new value)" % (o_index, param_name, param_value)
=======
                print "Modifying O_INDEX= %5d" % o_index
>>>>>>> zoo45xu/main
                print esa.updateValueAt(o_index, param_name, param_value)
                #self.list.SetItemBackgroundColour(line_index, 'Grey')
                n_checked += 1

        self.PushUpdate(event)

    def PushUpdate(self, event):
        conds = esa.getSortedDict()
        num = self.list.GetItemCount()

        packages = []
        gui_index = 0
        index_list = []


        for p in conds:
            ttt = (p['p_index'], p['isSkip'], p['isDS'], p['puckid'], p['pinid'], p['mode'],
                   p['score_min'], p['score_max'], p['maxhits'], p['dist_ds'],
                   p['cry_min_size_um'], p['cry_max_size_um'], p['loopsize'], p['n_mount'], p['isDone'], p['o_index'])

            index_list.append((p['p_index'], gui_index))
            packages.append(ttt)
            gui_index += 1

        line_index = 0
        for i in packages:
            p_index, isSkip, isDS, puckid, pinid, mode, score_min, \
            score_max, maxhits, dist_ds, cry_min_size_um, cry_max_size_um, loopsize, n_mount, isDone, o_index = i
            self.setValues(line_index, i, isInitial=False)
            line_index += 1
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

    def PushSkip(self, event):
        num = self.list.GetItemCount()
        for line_index in range(num):
            #print "PushSkip:"
            if self.list.IsChecked(line_index):
                # p_index=self.list.GetItemText(i,0)
                isSkip = 1
                # puck_id=self.list.GetItemText(i,3)
                # pin_id=self.list.GetItemText(i,4)
                # isSkip
                ichar = "%s" % isSkip
                self.list.SetStringItem(line_index, 2, ichar)
                # original index
                o_index = int(self.list.GetItemText(line_index, 1))
                print "O_INDEX= %5d is skipped" % o_index
                esa.updateValueAt(o_index, "isSkip", isSkip)
                self.list.SetItemBackgroundColour(line_index, 'Grey')

    def readValues(self, line_index):
        # Priority index
        p_index = int(self.list.GetItemText(line_index, 0))
        # o_index
        o_index = int(self.list.GetItemText(line_index, 1))
        # isSkip
        isSkip = int(self.list.GetItemText(line_index, 2))
        # isDS
        isDS = int(self.list.GetItemText(line_index, 3))
        # puckID
        puckID = self.list.GetItemText(line_index, 4)
        # pinID
        pinID = self.list.GetItemText(line_index, 5)
        # Scheme
        mode = self.list.GetItemText(line_index, 6)
        # score_min
        print "7=", self.list.GetItemText(line_index, 7)
        score_min = int(self.list.GetItemText(line_index, 7))
        # score_max
        score_max = int(self.list.GetItemText(line_index, 8))
        # max hit
        max_hits = int(self.list.GetItemText(line_index, 9))
        # dist for data collection
        dist_ds = float(self.list.GetItemText(line_index, 10))
        # Minimum crystal size
        cry_min_size = float(self.list.GetItemText(line_index, 11))
        # Minimum crystal size
        cry_max_size = float(self.list.GetItemText(line_index, 12))
        # Loop size
        loop_size = float(self.list.GetItemText(line_index, 13))
        # isDone
        isDone = int(self.list.GetItemText(line_index, 15))

        return p_index, o_index, isSkip, isDS, puckID, pinID, mode, score_min, score_max, max_hits, dist_ds, cry_min_size, cry_max_size, loop_size, isDone

    def OnApply(self, event):
        #logger.info("Event!!")
        n_data = self.list.GetItemCount()

        packages = []
        gui_index = 0
        index_list = []

        line_index = 0
        for i in range(0, n_data):
            p_index, o_index, isSkip, isDS, puckID, pinID, mode, score_min, score_max, max_hits, dist_ds, cry_min_size, cry_max_size, loop_size, isDone = self.readValues(
                i)
            print "mode=",mode
            print "score_min=",score_min
            esa.updateValueAt(o_index, "isSkip", isSkip)
            esa.updateValueAt(o_index, "p_index", p_index)
            #esa.updateValueAt(o_index, "mode", mode)
            esa.updateValueAt(o_index, "score_min", score_min)
            esa.updateValueAt(o_index, "score_max", score_max)
            esa.updateValueAt(o_index, "maxhits", max_hits)
            esa.updateValueAt(o_index, "cry_min_size_um", cry_min_size)
            esa.updateValueAt(o_index, "cry_max_size_um", cry_max_size)
            esa.updateValueAt(o_index, "loopsize", loop_size)
            esa.updateValueAt(o_index, "isDone", isDone)
            esa.updateValueAt(o_index, "dist_ds", dist_ds)
        self.PushUpdate(event)

<<<<<<< HEAD
    def calcTime(self):
        conds_dict = esa.getSortedDict()

        logline = ""
        lap_array = []
        n_collected = 0
        n_mounted = 0
        n_meas = 0
        n_planned = len(conds_dict)
        total_time = 0.0

        for each_db in conds_dict:
            isDone = each_db['isDone']
            if isDone == 0:
                continue

            dbinfo = DBinfo.DBinfo(each_db)
            pinstr = dbinfo.getPinStr()
            good_flag = dbinfo.getGoodOrNot()

            if dbinfo.isMount != 0:
                n_mounted += 1

            n_meas += 1
            mode = each_db['mode']
            nds = dbinfo.getNDS()
            constime = dbinfo.getMeasTime()

            if good_flag == True:
                logline += "%s OK. NDS(%8s) = %3d (%4.1f mins)\n" % (pinstr, mode, nds, constime)
            else:
                logline += "%s NG. %s\n" % (pinstr, dbinfo.getErrorMessage())

            total_time += constime

        # Mean measure time
        if n_meas != 0:
            mean_meas_time = total_time / float(n_meas)
        else:
            mean_meas_time = -999.9999

        n_remain = n_planned - n_mounted

        # Residual time
        residual_mins = mean_meas_time * n_remain
        residual_time = mean_meas_time * n_remain / 60.0  # hours

        logline += "Mean time/pin = %5.1f min.\n" % mean_meas_time
        logline += "Planned pins: %3d, Mounted(all): %3d, Remained: %3d\n" % (n_planned, n_mounted, n_remain)
        logline += "Expected remained time: %5.2f h  (%8.1f m)\n" % (residual_time, residual_mins)
        nowtime = datetime.datetime.now()
        exp_finish_time = nowtime + datetime.timedelta(hours=residual_time)
        logline += "Expected finishing time: %s\n" % (exp_finish_time)

        print logline

        if n_remain <= 1:
            logline += "Finished\n"

=======
>>>>>>> zoo45xu/main
    def UnsetSkip(self, event):
        num = self.list.GetItemCount()
        for line_index in range(num):
            if line_index == 0:
                self.log_window.Clear()
            if self.list.IsChecked(line_index):
                isSkip = 0
                ichar = "%s" % isSkip
                self.list.SetStringItem(line_index, 2, ichar)
                o_index = int(self.list.GetItemText(line_index, 1))
                esa.updateValueAt(o_index, "isSkip", isSkip)
                self.list.SetItemBackgroundColour(line_index, 'CYAN')

    def PushStartMod(self, event):
        print "UNKO SHIYOU"

app = wx.App()
Repository(None, -1, 'ENSOKU')
app.MainLoop()
