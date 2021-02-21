import wx

from about import AnimatedDialog

class SimpleTestFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, id=-1, title="Test Frame")

        btn_open = wx.Button(self, -1, "Open About Dialog")

        btn_open.Bind(wx.EVT_BUTTON, self._on_btn_open, btn_open)

        gs = wx.GridSizer(cols=1, rows=1, gap=(0, 0))
        gs.Add(btn_open, 0, wx.ALIGN_CENTER, 0)
        self.SetSizer(gs)

        self.SetSize((300, 200))
    
    def _on_btn_open(self, evt):
        dlg = AnimatedDialog(self, -1, "About Test",
        ["MyProgram.exe", "Mr Tester", "This is a simple App testing the AnimatedDialog", "0.1b"])
        dlg.ShowModal()
        dlg.Destroy()


def _test():
    app = wx.App()
    frame = SimpleTestFrame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    _test()