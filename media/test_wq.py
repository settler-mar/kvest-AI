import wx

app = wx.App()

# To get the count of displays
num_displays = wx.Display.GetCount()


class MyFrame(wx.Frame):
    def __init__(self, index):
        title = "Display %d" % display_num

        display = wx.Display(display_num)
        geometry = display.GetGeometry()
        wx.Frame.__init__(
            self,
            None,
            -1,
            title,
            geometry.GetTopLeft(),
            size=(300, 80),  # geometry.GetSize()
            style=wx.STAY_ON_TOP  # https://wxpython.org/Phoenix/docs/html/wx.Frame.html
        )

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(panel, -1, style=wx.ALIGN_CENTER)

        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        lbl.SetFont(font)
        lbl.SetLabel(title)

        box.Add(lbl, 0, wx.ALIGN_CENTER)
        lblwrap = wx.StaticText(panel, -1, style=wx.ALIGN_RIGHT)

        lblwrap.SetLabel('x={} y={}  res:{}x{}'.format(*geometry))
        lblwrap.Wrap(200)
        lblwrap.SetForegroundColour((255, 0, 0))
        font = self.GetFont()
        font.SetPointSize(14)
        lblwrap.SetFont(font)
        box.Add(lblwrap, 0, wx.ALIGN_LEFT)

        panel.SetSizer(box)
        # self.Centre()
        self.Show()


# Open a frame on each display
for display_num in range(num_displays):
    MyFrame(display_num)

app.MainLoop()
