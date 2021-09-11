#!/usr/bin/env python3

import sys
import os
import wx
from yaml_config import YamlConfig
import appdirs
from port_scan import *

import utils

class MainWindow(wx.Frame):

    def __init__(self, parent, title, configfile, appPath):
        self.configfile = configfile
        self.appPath = appPath
        self.init_settings()

        wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        mainpanel = wx.Panel(self)

        self.trans_button = wx.Button(mainpanel, label='Ok')
        self.trans_button.Bind(wx.EVT_BUTTON, self.find_port)

        self.text_output = wx.TextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        sizer = wx.GridBagSizer()
        sizer.Add(self.trans_button, pos=(0, 0), flag=wx.LEFT|wx.EXPAND)
        sizer.Add(self.text_output, pos=(0, 1), flag=wx.RIGHT|wx.EXPAND)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)
        mainpanel.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.SetMinSize((200, 200))
        self.SetSize((200, 200))
        self.Show(True)

    def close(self, event):
        pass

    def find_port(self, event):
        d = self.settings.value('gw')
        c = self.settings.value('community')
        m = self.settings.value('mac')

        #portscan = PortScan(device=d, community=c, mac=m)
        portscan = PortScan(help=True)
        out = utils.StringIO()
        with utils.captureStdOut(out):
            portscan.run()
        self.text_output.AppendText(out.getvalue())

    def init_settings(self):
        self.settings = YamlConfig(self.configfile)
        if not self.settings.value('gw'):
            self.settings.setValue('gw', '192.168.1.1')
        if not self.settings.value('community'):
            self.settings.setValue('community', 'public')
        if not self.settings.value('mac'):
            self.settings.setValue('mac', '00 00 00 00 00 00')


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
        appDataPath = appdirs.user_config_dir(appname, False)
        configfile =  os.path.join(appDataPath, 'settings.yaml')

        self.frame = MainWindow(None, title, configfile, appPath)
        return(True)

if __name__ == "__main__":
    app = MainApp(0)
    app.MainLoop()