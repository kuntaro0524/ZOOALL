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
        p['cry_min_size_um'],p['cry_max_size_um'],p['loopsize'],p['n_mount'])
    index_list.append((p['p_index'],gui_index))
    print(ttt)
    packages.append(ttt)
    gui_index+=1

class ChildFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self,parent,-1,"child frame",pos=(100,100))
        panel = wx.Panel(self)
        choice = wx.Choice(panel,-1)
        choice.Append('PriorityIndex',0)
        choice.Append('isSkip',0)
        choice.Append('isDS',0)
        choice.Append('puckID',0)
        choice.Append('pinID',0)
        choice.Append('Scheme',0)
        choice.Append('MinScore',0)
        choice.Append('MaxScore',0)
        choice.Append('MaxHit',0)
        choice.Append('DistDS',0)
        choice.Append('CryMinSize',0)
        choice.Append('CryMaxSize',0)
        choice.Append('LoopSize',0)
        choice.Append('n_mount',0)

        choice.Bind(wx.EVT_CHOICE, self.OnChoice)

        # Set sizer.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(choice, -1, wx.EXPAND|wx.ALL, 10)
        # Buttons
        updateButton = wx.Button(panel, -1, 'Update', size=(200, 300))
        self.Bind(wx.EVT_BUTTON, self.PushUpdate, id=updateButton.GetId())
        sizer.Add(updateButton)
        panel.SetSizer(sizer)

        # Parameter combo box
        element_array = ('10', '20', '30', '50', '100')
        combobox_1 = wx.ComboBox(panel, -1, 'Please select!', choices=element_array)

        sizer.Add(combobox_1)

    def OnChoice(self, event):
        choice = event.GetEventObject()
        n = choice.GetSelection()
        print(choice.GetString(n) + ', ' + choice.GetClientData(n))

    def PushUpdate(self, event):
        print("Push update!")

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
        self.list.InsertColumn(1, 'isSkip', width=50)
        self.list.InsertColumn(2, 'isDS', width=50)
        self.list.InsertColumn(3, 'puckID')
        self.list.InsertColumn(4, 'pinID')
        self.list.InsertColumn(5, 'Scheme')
        self.list.InsertColumn(6, 'MinScore')
        self.list.InsertColumn(7, 'MaxScore')
        self.list.InsertColumn(8, 'MaxHit')
        self.list.InsertColumn(9, 'DistDS')
        self.list.InsertColumn(10, 'CryMinSize')
        self.list.InsertColumn(11, 'CryMaxSize')
        self.list.InsertColumn(12, 'LoopSize')
        self.list.InsertColumn(13, 'n_mount')

        #ttt=(p['p_index'],p['isSkip'],p['puckid'],p['pinid'],p['mode'],
        #     p['score_max'],p['score_max'],p['maxhits'],p['dist_ds'],p['cry_min_size_um'],
        #     p['cry_max_size_um'],p['loopsize'],p['n_mount'])

        for i in packages:
            p_index,isSkip,isDS,puckid,pinid,mode,score_min,\
                score_max,maxhits,dist_ds,cry_min_size_um, cry_max_size_um,loopsize,n_mount = i

            #Priority index
            ichar = "%s"%p_index
            self.start_index = sys.maxsize
            index = self.list.InsertStringItem(sys.maxsize, ichar)
            # isSkip
            ichar = "%s"%isSkip
            self.list.SetStringItem(index, 1, ichar)

            if isSkip == 1 and isDS == 0: 
                self.list.SetItemBackgroundColour(index, 'Grey')
            elif isDS == 1:
                self.list.SetItemBackgroundColour(index, 'Green')
            elif isSkip == 0:
                self.list.SetItemBackgroundColour(index, 'Cyan')

            ichar = "%s"%isDS
            self.list.SetStringItem(index, 2, ichar)
            # puckID
            self.list.SetStringItem(index, 3, puckid)
            # pinID
            ichar = "%s"%pinid
            self.list.SetStringItem(index, 4, ichar)
            # Scheme
            self.list.SetStringItem(index, 5, mode)
            # score_min
            ichar = "%s"%score_min
            self.list.SetStringItem(index, 6, ichar)
            # score_max
            ichar = "%s"%score_max
            self.list.SetStringItem(index, 7, ichar)
            # max hit
            ichar = "%s"%maxhits
            self.list.SetStringItem(index, 8, ichar)
            # dist for data collection
            ichar = "%s"%dist_ds
            self.list.SetStringItem(index, 9, ichar)
            # min cry size
            ichar = "%s"%cry_min_size_um
            self.list.SetStringItem(index,10, ichar)
            # max cry size
            ichar = "%s"%cry_max_size_um
            self.list.SetStringItem(index,11, ichar)
            # Loop size
            loop_char = "%5.1f"%loopsize
            self.list.SetStringItem(index,12, loop_char)
            # nMount
            ichar = "%s"%n_mount
            self.list.SetStringItem(index,13, ichar)

        vbox2 = wx.BoxSizer(wx.VERTICAL)

        sel = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
        des = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))
        apply = wx.Button(leftPanel, -1, 'Apply', size=(100, -1))
        setskip = wx.Button(leftPanel, -1, 'set SKIP', size=(100, -1))
        unsetskip = wx.Button(leftPanel, -1, 'unset SKIP', size=(100, -1))
        updateButton = wx.Button(leftPanel, -1, 'Update', size=(100, -1))
        modButton = wx.Button(leftPanel, -1, 'Modify', size=(100, -1))

        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=sel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=des.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=apply.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushSkip, id=setskip.GetId())
        self.Bind(wx.EVT_BUTTON, self.UnsetSkip, id=unsetskip.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushUpdate, id=updateButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.PushMod, id=modButton.GetId())

        vbox2.Add(sel, 0, wx.TOP, 5)
        vbox2.Add(des)
        vbox2.Add(apply)
        vbox2.Add(setskip)
        vbox2.Add(unsetskip)
        vbox2.Add(updateButton)
        vbox2.Add(modButton)

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
        ppp = esa.getDict()
        num = self.list.GetItemCount()

        packages = []
        gui_index = 0
        index_list = []

        for p in ppp:
            ttt = (p['p_index'], p['isSkip'], p['isDS'], p['puckid'], p['pinid'], p['mode'],
                   p['score_min'], p['score_max'], p['maxhits'], p['dist_ds'],
                   p['cry_min_size_um'], p['cry_max_size_um'], p['loopsize'], p['n_mount'])
            index_list.append((p['p_index'], gui_index))
            packages.append(ttt)
            gui_index += 1

        line_index = 0
        for i in packages:
            p_index, isSkip, isDS, puckid, pinid, mode, score_min, \
            score_max, maxhits, dist_ds, cry_min_size_um, cry_max_size_um, loopsize, n_mount = i

            # Priority index
            ichar = "%s" % p_index
            self.list.SetStringItem(line_index, 0, ichar)

            # isSkip
            ichar = "%s" % isSkip
            self.list.SetStringItem(line_index, 1, ichar)

            if isSkip == 1 and isDS == 0:
                self.list.SetItemBackgroundColour(line_index, 'Grey')
            elif isDS == 1:
                self.list.SetItemBackgroundColour(line_index, 'Green')
            ichar = "%s" % isDS
            self.list.SetStringItem(line_index, 2, ichar)
            # puckID
            self.list.SetStringItem(line_index, 3, puckid)
            # pinID
            ichar = "%s" % pinid
            self.list.SetStringItem(line_index, 4, ichar)
            # Scheme
            self.list.SetStringItem(line_index, 5, mode)
            # score_min
            ichar = "%s" % score_min
            self.list.SetStringItem(line_index, 6, ichar)
            # score_max
            ichar = "%s" % score_max
            self.list.SetStringItem(line_index, 7, ichar)
            # max hit
            ichar = "%s" % maxhits
            self.list.SetStringItem(line_index, 8, ichar)
            # dist for data collection
            ichar = "%s" % dist_ds
            self.list.SetStringItem(line_index, 9, ichar)
            # min cry size
            ichar = "%s" % cry_min_size_um
            self.list.SetStringItem(line_index, 10, ichar)
            # max cry size
            ichar = "%s" % cry_max_size_um
            self.list.SetStringItem(line_index, 11, ichar)
            # Loop size
            loop_char = "%5.1f" % loopsize
            self.list.SetStringItem(line_index, 12, loop_char)
            # nMount
            ichar = "%s" % n_mount
            self.list.SetStringItem(line_index, 13, ichar)
            line_index += 1

    def readCurrentSkipList(self):
        num = self.list.GetItemCount()
        for n_column in range(num):
            # isSkip
            print("Reading")
            print(self.list.GetItemText(n_column, 1))

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
            print("PushSkip:")
            if self.list.IsChecked(i): 
                #p_index=self.list.GetItemText(i,0)
                isSkip = 1
                #puck_id=self.list.GetItemText(i,3)
                #pin_id=self.list.GetItemText(i,4)
                # isSkip
                ichar = "%s"%isSkip
                print("PushSkip:selected = ",i, isSkip)
                print("ichar = ", ichar)
                self.list.SetStringItem(i, 1, ichar)
                pindex = i
                esa.updateValueAt(pindex,"isSkip", isSkip)
                self.list.SetItemBackgroundColour(i, 'Grey')

    def OnApply(self, event):
        print("##########################")
        self.readCurrentSkipList()
        print("##########################")

        num = self.list.GetItemCount()
        for i in range(num):
            print(i)
            if i == 0: 
                self.log.Clear()
            print(self.list[i])

    def UnsetSkip(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            #print "PushSkip:", i
            if i == 0:
                self.log.Clear()
            if self.list.IsChecked(i):
                isSkip = 0
                ichar = "%s"%isSkip
                print("PushSkip:selected = ",i, isSkip)
                print("ichar = ", ichar)
                self.list.SetStringItem(i, 1, ichar)
                pindex = i
                print("PINDEX=",pindex)
                esa.updateValueAt(pindex,"isSkip", isSkip)
                self.list.SetItemBackgroundColour(i, 'CYAN')


    def DialogYesNo(self, event):
        dialog = wx.MessageDialog(None, 'Yes or No?', 'Checkout your affiliation.',
                                  style=wx.YES_NO | wx.ICON_INFORMATION)
        res = dialog.ShowModal()
        dialog.Destroy()

        if res == wx.ID_YES:
            return True
        elif res == wx.ID_NO:
            return False

    def DialogError(self, event):
        dialog = wx.MessageDialog(None, 'OK', 'Checkout your affiliation.', style=wx.OK)
        res = dialog.ShowModal()
        dialog.Destroy()
        dialog = wx.MessageDialog(None, 'CANCEL', 'Checkout your affiliation.', style=wx.CANCEL)
        res = dialog.ShowModal()
        dialog.Destroy()

    def PushMod(self,event):
        print("PUSHMOD")
        num = self.list.GetItemCount()
        list_selected=[]
        for i in range(num):
            if self.list.IsChecked(i):
                list_selected.append(i)
        if len(list_selected) == 0:
            print("nothing to do")
            return

        childFrame = MyDialog(self, list_selected, self.list)
 
class MyDialog(wx.Frame):
    def __init__(self, parent, list_selected, list_window):
        self.list_window = list_window
        self.list_sel = list_selected
        wx.Frame.__init__(self,parent,-1,"main frame",size=(800,800))
        panel = wx.Panel(self)
        self.element_array = ('PriorityIndex', 'isSkip', 'isDS', 'puckID', 
            'pinID', 'Scheme', 'MinScore', 'MaxScore', 'MaxHit', 'DistDS', 'CryMinSize', 'CryMaxSize', 'LoopSize', 'n_mount')
        self.choice_1 = wx.Choice(panel, wx.ID_ANY, choices=self.element_array)
        self.setButton = wx.Button(panel, wx.ID_ANY, "Set values")
        self.cancelButton = wx.Button(panel, wx.ID_ANY, "Cancel")
        value_array = ('10', '20', '30', '50', '100')
        self.combo_box_1 = wx.ComboBox(panel, wx.ID_ANY, 'SELECT!', choices=value_array, style=wx.CB_DROPDOWN)
        #wx.ALIGN_CENTER
        #self.combo_box_1 = wx.ComboBox(panel, wx.ID_ANY, 'SELECT!', choices=element_array)

        if self.FindWindowByName('Setting') is None:
            self.Show()
            self.__set_properties()
            self.__do_layout()
            # BINDING
            self.Bind(wx.EVT_BUTTON, self.PushSet, id=self.setButton.GetId())
            self.Bind(wx.EVT_BUTTON, self.PushCancel, id=self.cancelButton.GetId())
        else:
            dialog = wx.MessageDialog(self, 'Existing!', 'Error', wx.ICON_ERROR) 
            dialog.ShowModal() 
            dialog.Destroy()

        # end wxGlade
    def PushSet(self, event):
        n = self.choice_1.GetSelection()
        print(self.element_array[n])
        value = self.combo_box_1.GetValue()
        # max hit
        #ichar = "%s" % value
        for i in self.list_sel:
            print("MOD", i)
            self.list_window.SetStringItem(i, n, value)

        print("PUSHSET")

    def PushCancel(self, event):
        self.Destroy()

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle('Setting')
        self.choice_1.SetMinSize((200, 30))
        self.choice_1.SetSelection(0)
        self.setButton.SetMinSize((200, 30))
        self.combo_box_1.SetMinSize((200, 30))
        self.cancelButton.SetMinSize((200, 30))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        strings = "selected items: %s" % self.list_sel
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        label_3 = wx.StaticText(self, wx.ID_ANY, strings)
        label_3.SetMinSize((300, 30))
        sizer_3.Add(label_3, 0, wx.ALIGN_CENTER, 0)
        label_1 = wx.StaticText(self, wx.ID_ANY, "Select")
        label_1.SetMinSize((200, 30))
        sizer_3.Add(label_1, 0, wx.ALIGN_CENTER, 0)
        label_2 = wx.StaticText(self, wx.ID_ANY, "Change buttons")
        label_2.SetMinSize((200, 30))
        sizer_3.Add(label_2, 0, wx.ALIGN_CENTER, 0)
        #sizer_2.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        label_4 = wx.StaticText(self, wx.ID_ANY, "Choose parameter")
        label_4.SetMinSize((200, 30))
        sizer_4.Add(label_4, 0, wx.ALIGN_CENTER, 0)
        sizer_4.Add(self.choice_1, 0, 0, 0)
        sizer_4.Add(self.setButton, 0, 0, 0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
        label_5 = wx.StaticText(self, wx.ID_ANY, "Input Value")
        label_5.SetMinSize((200, 30))
        sizer_5.Add(label_5, 0, wx.ALIGN_CENTER, 0)
        sizer_5.Add(self.combo_box_1, 0, 0, 0)
        sizer_5.Add(self.cancelButton, 0, 0, 0)
        sizer_2.Add(sizer_5, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
        # end wxGlade
# end of class MyApp
app = wx.App()
Repository(None, -1, 'ENSOKU')
app.MainLoop()

