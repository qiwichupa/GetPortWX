#!/usr/bin/env python3

import sys
import os
import wx
from yaml_config import YamlConfig


class MainWindow(wx.Frame):

    def __init__(self, parent, title, configfile):
        self.configfile = configfile
        self.init_settings()

        wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        mainpanel = wx.Panel(self)

        self.trans_button = wx.Button(mainpanel, label='Ok')
        self.trans_button.Bind(wx.EVT_BUTTON, self.close)

        sizer = wx.GridBagSizer()
        sizer.Add(self.trans_button, pos=(0, 0), flag=wx.RIGHT|wx.EXPAND)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)
        mainpanel.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.SetMinSize((200, 200))
        self.SetSize((200, 200))
        self.Show(True)

    def close(self, event):
        pass

    def init_settings(self):
        self.settings = YamlConfig(self.configfile)
        if not self.settings.value('gw'):
            self.settings.setValue('gw', '192.168.1.1')


class MainApp(wx.App):
    def OnInit(self):
        appname = "catalystmacfinder"
        ver = "0.1"
        title = '{n} (v.{v})'.format(n=appname, v=ver)

        # get path of program dir.
        # sys._MEIPASS - variable of pyinstaller (one-dir package) with path to executable
        try:
            sys._MEIPASS
            appPath = sys._MEIPASS
        except:
            appPath = os.path.dirname(os.path.abspath(__file__))
        # set "data" in program dir as working directory
        appDataPath = os.path.join(appPath, "data")
        try:
            os.makedirs(appDataPath, exist_ok=True)
        except:
            appDataPath = appPath
        configfile =  os.path.join(appDataPath, 'settings.yaml')

        self.frame = MainWindow(None, title, configfile)
        return(True)

if __name__ == "__main__":
    app = MainApp(0)
    app.MainLoop()