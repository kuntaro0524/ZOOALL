#!/usr/bin/python
import wx
import sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import wx.lib.mixins.listctrl as listmix
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

import ESA

esa=ESA.ESA(sys.argv[1])
esa.listDB()
ppp = esa.getDict()

packages=[]
gui_index=0
index_list=[]
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
    ttt=(p['p_index'],p['isSkip'],p['isDS'],p['puckid'],p['pinid'],p['mode'],
        p['score_min'],p['score_max'],p['maxhits'],p['dist_ds'],
        p['cry_min_size_um'],p['cry_max_size_um'],p['loopsize'],p['n_mount'],p['isDone'],p['o_index'])
    index_list.append((p['p_index'],gui_index))
    print ttt
    packages.append(ttt)
    gui_index+=1

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin,listmix.CheckListCtrlMixin):
    ''' TextEditMixin allows any column to be edited. '''
    #----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)
        listmix.CheckListCtrlMixin.__init__(self)

class Repository(wx.Frame):

    def setValues(self, index, param_list, isInitial = True):
        p_index, isSkip, isDS, puckid, pinid, mode, score_min, \
        score_max, maxhits, dist_ds, cry_min_size_um, cry_max_size_um, loopsize, n_mount, isDone, o_index = param_list

        # Priority index
        ichar = "%s" % p_index
        self.start_index = sys.maxint
        index = self.list.InsertStringItem(sys.maxint, ichar)

        # o_index
        ichar = "%s" % o_index
        self.list.SetStringItem(index, 1, ichar)

        # isSkip
        ichar = "%s" % isSkip
        self.list.SetStringItem(index, 2, ichar)

        if isSkip == 1 and isDS == 0:
            self.list.SetItemBackgroundColour(index, 'Grey')
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
        ichar = "%s" % score_min
        self.list.SetStringItem(index, 7, ichar)
        # score_max
        ichar = "%s" % score_max
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

        self.log = wx.TextCtrl(rightPanel, -1, style=wx.TE_MULTILINE)
        self.list = EditableListCtrl(rightPanel,0,size=(300,100),style=wx.LC_REPORT|wx.LC_HRULES)
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

        #ttt=(p['p_index'],p['isSkip'],p['puckid'],p['pinid'],p['mode'],
        #     p['score_max'],p['score_max'],p['maxhits'],p['dist_ds'],p['cry_min_size_um'],
        #     p['cry_max_size_um'],p['loopsize'],p['n_mount'])

        line_index = 0
        for i in packages:
            p_index,isSkip,isDS,puckid,pinid,mode,score_min,\
                score_max,maxhits,dist_ds,cry_min_size_um, cry_max_size_um,loopsize,n_mount,isDone, o_index = i
            self.setValues(line_index, i)
            line_index += 1

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
        conds = esa.getDict()
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
            p_index,isSkip,isDS,puckid,pinid,mode,score_min,\
                score_max,maxhits,dist_ds,cry_min_size_um, cry_max_size_um,loopsize,n_mount,isDone, o_index = i

            # Priority index
            ichar = "%s" % p_index
            self.list.SetStringItem(line_index, 0, ichar)
            # Priority index
            ichar = "%s" % o_index
            self.list.SetStringItem(line_index, 1, ichar)

            # isSkip
            ichar = "%s" % isSkip
            self.list.SetStringItem(line_index, 2, ichar)

            if isSkip == 1 and isDS == 0:
                self.list.SetItemBackgroundColour(index, 'Grey')
            elif isDone == 1:
                self.list.SetItemBackgroundColour(index, 'Green')
            elif isDone > 1000:
                self.list.SetItemBackgroundColour(index, 'Orange')
            elif isSkip == 0 and isDS == 0:
                self.list.SetItemBackgroundColour(index, 'Cyan')

            ichar = "%s"%isDS
            self.list.SetStringItem(line_index, 3, ichar)
            # puckID
            self.list.SetStringItem(line_index, 4, puckid)
            # pinID
            ichar = "%s"%pinid
            self.list.SetStringItem(line_index, 5, ichar)
            # Scheme
            self.list.SetStringItem(line_index, 6, mode)
            # score_min
            ichar = "%s"%score_min
            self.list.SetStringItem(line_index, 7, ichar)
            # score_max
            ichar = "%s"%score_max
            self.list.SetStringItem(line_index, 8, ichar)
            # max hit
            ichar = "%s"%maxhits
            self.list.SetStringItem(line_index, 9, ichar)
            # dist for data collection
            ichar = "%s"%dist_ds
            self.list.SetStringItem(line_index,10, ichar)
            # min cry size
            ichar = "%s"%cry_min_size_um
            self.list.SetStringItem(line_index,11, ichar)
            # max cry size
            ichar = "%s"%cry_max_size_um
            self.list.SetStringItem(line_index,12, ichar)
            # Loop size
            loop_char = "%5.1f"%loopsize
            self.list.SetStringItem(line_index,13, loop_char)
            # nMount
            ichar = "%s"%n_mount
            self.list.SetStringItem(line_index,14, ichar)
            # isDone
            ichar = "%s"%isDone
            self.list.SetStringItem(line_index,15, ichar)

            line_index += 1

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
        for i in range(num):
            print "PushSkip:"
            if self.list.IsChecked(i): 
                #p_index=self.list.GetItemText(i,0)
                isSkip = 1
                #puck_id=self.list.GetItemText(i,3)
                #pin_id=self.list.GetItemText(i,4)
                # isSkip
                ichar = "%s"%isSkip
                print "PushSkip:selected = ",i, isSkip
                print "ichar = ", ichar
                self.list.SetStringItem(i, 1, ichar)
                pindex = i
                esa.updateValueAt(pindex,"isSkip", isSkip)
                self.list.SetItemBackgroundColour(i, 'Grey')

    def OnApply(self, event):
        n_data = self.list.GetItemCount()

        packages = []
        gui_index = 0
        index_list = []

        line_index = 0
        for i in range(0, n_data):
            #p_index,isSkip,isDS,puckid,pinid,mode,score_min,\
            #    score_max,maxhits,dist_ds,cry_min_size_um, cry_max_size_um,loopsize,n_mount,isDone = i

            # Priority index
            ichar = self.list.GetItemText(line_index, 0)
            print "ICHAR=", ichar
            print "P_INDEX= %5d" % int(ichar)


    def UnsetSkip(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            #print "PushSkip:", i
            if i == 0:
                self.log.Clear()
            if self.list.IsChecked(i):
                isSkip = 0
                ichar = "%s"%isSkip
                print "PushSkip:selected = ",i, isSkip
                print "ichar = ", ichar
                self.list.SetStringItem(i, 1, ichar)
                pindex = i
                print "PINDEX=",pindex
                esa.updateValueAt(pindex,"isSkip", isSkip)
                self.list.SetItemBackgroundColour(i, 'CYAN')

app = wx.App()
Repository(None, -1, 'ENSOKU')
app.MainLoop()
