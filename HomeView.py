import wx
from P2PView import MyFrameTest

class MyTab1(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.my_frame = MyFrameTest(self)  # Передаем текущий wx.Panel как родительский элемент
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.my_frame, 1, wx.EXPAND)
        self.SetSizer(sizer)

class MyTab2(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        # Создайте здесь интерфейс для второй вкладки

class MyTab3(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        # Создайте здесь интерфейс для третьей вкладки

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="АРБИТРАЖ - 3000")
        self.Maximize() 
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        notebook = wx.Notebook(panel)

        tab1 = MyTab1(notebook)
        notebook.AddPage(tab1, "p2p как мейкер")

        tab2 = MyTab2(notebook)
        notebook.AddPage(tab2, "Вторая вкладка")

        tab3 = MyTab3(notebook)
        notebook.AddPage(tab3, "Третья вкладка")

        vbox.Add(notebook, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Создаем кнопку "Выход"
        exit_button = wx.Button(panel, label="Выход")
        exit_button.Bind(wx.EVT_BUTTON, self.on_exit)
        vbox.Add(exit_button, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.Center()

    def on_exit(self, event):
        self.Close()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
