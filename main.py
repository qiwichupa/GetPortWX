#!/usr/bin/env python3

import re
import os
import wx
from yaml_config import YamlConfig
import appdirs
import regex
from port_scan import *

import utils


class IPValidator(wx.Validator):
    """ This validator is used to ensure that the user has entered a float
        into the text control of MyFrame.
    """

    def __init__(self):
        """ Standard constructor.
        """
        wx.Validator.__init__(self)

    def Clone(self):
        """ Standard cloner.

            Note that every validator must implement the Clone() method.
        """
        return IPValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        string = textCtrl.GetValue().strip()
        pattern = "^((25[0-5]|2[0-4][0-9]|[01]?[0-9]{1,2})\.){3}(?2)$"
        if regex.match(pattern, string):
            textCtrl.SetValue(string)
            return True
        else:
            return False

    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        """ Transfer data from window to validator.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

class MACValidator(wx.Validator):
    """ This validator is used to ensure that the user has entered a float
        into the text control of MyFrame.
    """

    def __init__(self):
        """ Standard constructor.
        """
        wx.Validator.__init__(self)

    def Clone(self):
        """ Standard cloner.

            Note that every validator must implement the Clone() method.
        """
        return MACValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        try:
            string = self.format_mac(textCtrl.GetValue())
        except:
            return False
        else:
            textCtrl.SetValue(string)
            return True

    def format_mac(self, mac: str) -> str:
        mac = re.sub('[.:-]', '', mac).lower()  # remove delimiters and convert to lower case
        mac = ''.join(mac.split())  # remove whitespaces
        assert len(mac) == 12  # length should be now exactly 12 (eg. 008041aefd7e)
        assert mac.isalnum()  # should only contain letters and numbers
        # convert mac in canonical form (eg. 00:80:41:ae:fd:7e)
        mac = ":".join(["%s" % (mac[i:i + 2]) for i in range(0, 12, 2)])
        return mac


    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        """ Transfer data from window to validator.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

class MainWindow(wx.Frame):

    def __init__(self, parent, title, configfile, appPath):
        self.configfile = configfile
        self.appPath = appPath

        wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        mainpanel = wx.Panel(self)

        self.spacer = wx.StaticText(mainpanel, label="")

        self.device_label = wx.StaticText(mainpanel, label="Router:")
        self.device_ctrl = wx.TextCtrl(mainpanel, size=(150, -1), validator=IPValidator())
        self.device_ctrl.Bind(wx.EVT_TEXT, self.settings_save_device)

        self.community_label = wx.StaticText(mainpanel, label="SNMP community:")
        self.community_ctrl = wx.TextCtrl(mainpanel, size=(150, -1))
        self.community_ctrl.Bind(wx.EVT_TEXT, self.settings_save_community)

        self.mac_label = wx.StaticText(mainpanel,  label="Search MAC address:")
        self.mac_ctrl = wx.TextCtrl(mainpanel, size=(150, -1), validator=MACValidator())
        self.mac_ctrl.Bind(wx.EVT_TEXT, self.settings_save_mac)

        self.ip_label = wx.StaticText(mainpanel, label="Search IP:")
        self.ip_ctrl = wx.TextCtrl(mainpanel, size=(150, -1), validator=IPValidator())
        self.ip_ctrl.Bind(wx.EVT_TEXT, self.settings_save_ip)

        self.trans_button = wx.Button(mainpanel, label='Ok')
        self.trans_button.Bind(wx.EVT_BUTTON, self.find_port)

        self.text_output = wx.TextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        sizer = wx.GridBagSizer()

        sizer.Add(self.device_label,  pos=(0, 0), flag=wx.ALIGN_BOTTOM)
        sizer.Add(self.device_ctrl, pos=(1, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.community_label, pos=(2, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.community_ctrl, pos=(3, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.mac_label, pos=(4, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.mac_ctrl, pos=(5, 0), flag=wx.ALIGN_TOP )
        sizer.Add(self.ip_label, pos=(6, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.ip_ctrl, pos=(7, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.trans_button, pos=(8, 0), flag=wx.ALIGN_TOP | wx.EXPAND)

        sizer.Add(self.text_output, pos=(0, 1), span=(10, 1), flag= wx.ALIGN_TOP | wx.EXPAND)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)
        mainpanel.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        x, y = sizer.GetSize()
        x+=300
        y+=150
        self.SetMinSize((x, y))
        self.SetSize((x, y))

        self.init_settings()

        self.Show(True)

    def close(self, event):
        pass


    def find_port(self, event):
        if len(self.mac_ctrl.GetValue().strip()) == 0 or self.mac_ctrl.GetValidator().Validate(self.mac_ctrl):
            pass
        else:
            self.text_output.AppendText("Not valid MAC\n")
            self.separator()
            return

        if len(self.ip_ctrl.GetValue().strip()) == 0 or self.ip_ctrl.GetValidator().Validate(self.ip_ctrl):
            pass
        else:
            self.text_output.AppendText("Not valid IP\n")
            self.separator()
            return

        if self.device_ctrl.GetValidator().Validate(self.device_ctrl):
            pass
        else:
            self.text_output.AppendText("Not valid router IP\n")
            self.separator()
            return

        device = self.device_ctrl.GetValue()
        community = self.community_ctrl.GetValue()
        mac = self.mac_ctrl.GetValue()
        ip = self.ip_ctrl.GetValue()

        portscan = PortScan(device=device, community=community, mac=mac, ip = ip)
        out = utils.StringIO()
        with utils.captureStdOut(out):
            portscan.run()
        self.text_output.AppendText(out.getvalue())
        self.separator()

    def settings_save_device(self, event):
        self.settings.setValue('device', self.device_ctrl.GetValue())

    def settings_save_mac(self, event):
        self.settings.setValue('mac', self.mac_ctrl.GetValue())

    def settings_save_community(self, event):
        self.settings.setValue('community', self.community_ctrl.GetValue())

    def settings_save_ip(self, event):
        self.settings.setValue('ip', self.ip_ctrl.GetValue())

    def init_settings(self):
        self.settings = YamlConfig(self.configfile)
        if not self.settings.value('device'):
            self.settings.setValue('device', '192.168.1.1')
        if not self.settings.value('community'):
            self.settings.setValue('community', 'public')
        '''
        if not self.settings.value('mac'):
            self.settings.setValue('mac', '00 00 00 00 00 00')
        if not self.settings.value('ip'):
            self.settings.setValue('ip', '1.2.3.4')
        '''
        self.device_ctrl.SetValue(self.settings.value('device'))
        self.community_ctrl.SetValue(self.settings.value('community'))
        '''
        self.mac_ctrl.SetValue(self.settings.value('mac'))
        self.ip_ctrl.SetValue(self.settings.value('ip'))
        '''

    def separator(self):
        self.text_output.AppendText("=======================\n\n")


class MainApp(wx.App):
    def OnInit(self):
        appname = "GetPortWX"
        ver = "1.0-rc1"
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