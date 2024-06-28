import wx

def click(event):
    dlg = wx.TextEntryDialog(None, u'Exciting')
    dlg.ShowModal()
    dlg.Destroy()

    input_text = dlg.GetValue()
    frame.SetStatusText(input_text)

app = wx.App()

frame = wx.Frame(None, -1, u'MainFrame', size=(200, 200))
frame.CreateStatusBar()
p = wx.Panel(frame, -1)

button = wx.Button(p, -1, u'Button')
button.Bind(wx.EVT_BUTTON, click)

frame.Show()
app.MainLoop()
