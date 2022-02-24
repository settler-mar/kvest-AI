import wx


class MyPanel(wx.Panel):
    """"""

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.Bind(wx.EVT_KEY_DOWN, self.onKey)

    def onKey(self, event):
        """
        Check for ESC key press and exit is ESC is pressed
        F1 panel 1 is full screen
        F2 panel 2 is full screen
        F3 panels revert to equal sizes
        """
        key_code = event.GetKeyCode()
        parent = self.GetParent()
        width, height = wx.GetDisplaySize()
        if key_code == wx.WXK_ESCAPE:
            self.GetParent().Close()
        elif key_code == wx.WXK_F1:
            parent.panel1.SetMinSize((1, 1))
            parent.panel2.SetMinSize((width, height))
            parent.SendSizeEvent()
            parent.Layout()
            parent.Fit()
        elif key_code == wx.WXK_F2:
            parent.panel2.SetMinSize((1, 1))
            parent.panel1.SetMinSize((width, height))
            parent.SendSizeEvent()
            parent.Layout()
            parent.Fit()
        else:
            event.Skip()


class MyFrame(wx.Frame):
    """"""

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, -1, title="Test FullScreen", style=wx.STAY_ON_TOP)
        self.panel1 = MyPanel(self)
        self.panel2 = MyPanel(self)
        self.panel1.SetBackgroundColour(wx.GREEN)
        self.panel2.SetBackgroundColour(wx.BLUE)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.panel1)
        vbox.Add(self.panel2)
        self.SetSizer(vbox)
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
