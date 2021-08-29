#!/usr/bin/env python3

import sys
import os
import wx
import yaml

class MainWindow(wx.Frame):

    def __init__(self, parent, title, configfile):
        wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)

        self.configfile = configfile
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
        self.settings_init()

    def close(self, event):
        pass

    def settings_init(self):
        '''Load settings and create default parameters'''
        self.settings_load()
        if type(self.settings) is not dict:
            self.settings = {}
        try:
            type(self.settings['gw'])
        except:
            self.settings['gw'] = '192.168.1.1'
        self.settings_save()

    def settings_load(self):
        try:
            with open(self.configfile) as f:
                self.settings = yaml.load(f, Loader=yaml.FullLoader)
        except:
            with open(self.configfile, 'w') as f:
                f.write('')
            with open(self.configfile) as f:
                self.settings = yaml.load(f, Loader=yaml.FullLoader)

    def settings_save(self):
        with open(self.configfile, 'w') as f:
            self.settings = yaml.dump(self.settings, stream=f,
                               default_flow_style=False, sort_keys=False)

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