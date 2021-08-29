#!/usr/bin/env python3

import sys
import os
import wx
import yaml

class YamlConfig():
    def __init__(self, configfile):
        self.configfile = configfile
        # check|create dir
        try:
            os.makedirs(os.path.dirname(self.configfile),exist_ok=True)
        except Exception as e:
            print(e)
        # check|create file
        try:
            with open(self.configfile) as f:
                self.settings = yaml.load(f, Loader=yaml.FullLoader)
        except:
            with open(self.configfile, 'w') as f:
                f.write('')

    def __readconf__(self):
        with open(self.configfile) as f:
            self.settings = yaml.load(f, Loader=yaml.FullLoader)
        if type(self.settings) is not dict:
            self.settings = {}

    def load(self, option):
        self.__readconf__()
        try:
            type(settings[option])
            return(str(settings[option]))
        except:
            return(None)

    def save(self, option, value):
        self.__readconf__()
        self.settings[option] = value
        with open(self.configfile, 'w') as f:
            self.settings = yaml.dump(self.settings, stream=f,
                               default_flow_style=False, sort_keys=False)


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
        if self.settings.load('gw') is None:
            self.settings.save('gw', '192.168.1.1')


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