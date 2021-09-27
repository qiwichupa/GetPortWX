#!/usr/bin/env python3

import time
import wx
import wx.lib.agw.hyperlink as hl

from yaml_config import YamlConfig
from app_dirs import AppDirs
import utils
from port_scan import *

import regex
from threading import Thread, Event
from pubsub import pub as Publisher


class SearchAnimation(Thread):
    """Search Button 'Searching..' Animation Thread."""

    def __init__(self):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.kill = Event()

    # ----------------------------------------------------------------------
    def run(self):
        seconds = 0
        interval = 1
        while not self.kill.is_set():
            timer = time.strftime('%M:%S', time.gmtime(seconds))
            label = "({t}) Searching...".format(t=timer)
            wx.CallAfter(Publisher.sendMessage, "animate", msg=label)
            time.sleep(interval)
            seconds = seconds + interval


class GetPortThread(Thread):
    """Main Thread: runs original python script with parameters"""

    # ----------------------------------------------------------------------
    def __init__(self, device, community, mac, ip):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.device = device
        self.community = community
        self.mac = mac
        self.ip = ip

    # ----------------------------------------------------------------------
    def run(self):
        portscan = PortScan(device=self.device, community=self.community,
                            mac=self.mac, ip=self.ip)
        out = utils.StringIO()
        with utils.captureStdOut(out):
            portscan.run()
        msg = out.getvalue()
        wx.CallAfter(Publisher.sendMessage, "update", msg=msg)


class IPValidator(wx.Validator):
    """ WX validator for IP-inputs """

    # ----------------------------------------------------------------------
    def __init__(self):
        wx.Validator.__init__(self)

    # ----------------------------------------------------------------------
    def Clone(self):
        return IPValidator()

    # ----------------------------------------------------------------------
    def Validate(self, win):
        textCtrl = self.GetWindow()
        string = textCtrl.GetValue().strip()
        pattern = "^((25[0-5]|2[0-4][0-9]|[01]?[0-9]{1,2})\.){3}(?2)$"
        if regex.match(pattern, string):
            textCtrl.SetValue(string)
            return True
        else:
            return False

    # ----------------------------------------------------------------------
    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

    # ----------------------------------------------------------------------
    def TransferFromWindow(self):
        """ Transfer data from window to validator.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.


class MACValidator(wx.Validator):
    """ WX validator for MAC-address input.
        Also converts a correct MAC to canonical form and return it
    """

    # ----------------------------------------------------------------------
    def __init__(self):

        wx.Validator.__init__(self)

    # ----------------------------------------------------------------------
    def Clone(self):
        return MACValidator()

    # ----------------------------------------------------------------------
    def Validate(self, win):
        textCtrl = self.GetWindow()
        # noinspection PyBroadException
        try:
            string = self.format_mac(textCtrl.GetValue())
        except Exception:
            return False
        else:
            textCtrl.SetValue(string)
            return True

    # ----------------------------------------------------------------------
    def format_mac(self, mac: str) -> str:
        mac = re.sub('[.:-]', '', mac).lower()  # remove delimiters and convert to lower case
        mac = ''.join(mac.split())  # remove whitespaces
        assert len(mac) == 12  # length should be now exactly 12 (eg. 008041aefd7e)
        assert mac.isalnum()  # should only contain letters and numbers
        # convert mac in canonical form (eg. 00:80:41:ae:fd:7e)
        mac = ":".join(["%s" % (mac[i:i + 2]) for i in range(0, 12, 2)])
        return mac

    # ----------------------------------------------------------------------
    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

    # ----------------------------------------------------------------------
    def TransferFromWindow(self):
        """ Transfer data from window to validator.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.


class MainWindow(wx.Frame):
    # ----------------------------------------------------------------------
    def __init__(self, parent, title, configfile):
        self.configfile = configfile

        wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        mainpanel = wx.Panel(self)

        self.info = hl.HyperLinkCtrl(mainpanel, -1, label="Project on Github",
                                     URL="https://github.com/qiwichupa/GetPortWX")

        self.device_label = wx.StaticText(mainpanel, label="Router:")
        self.device_ctrl = wx.TextCtrl(mainpanel, size=(150, -1), validator=IPValidator())
        self.device_ctrl.Bind(wx.EVT_TEXT, self.settings_save_device)

        self.community_label = wx.StaticText(mainpanel, label="SNMP community:")
        self.community_ctrl = wx.TextCtrl(mainpanel, size=(150, -1))
        self.community_ctrl.Bind(wx.EVT_TEXT, self.settings_save_community)

        self.mac_label = wx.StaticText(mainpanel, label="Search MAC address:")
        self.mac_ctrl = wx.TextCtrl(mainpanel, size=(150, -1), validator=MACValidator())
        self.mac_ctrl.Bind(wx.EVT_TEXT, self.settings_save_mac)

        self.ip_label = wx.StaticText(mainpanel, label="Search IP:")
        self.ip_ctrl = wx.TextCtrl(mainpanel, size=(150, -1), validator=IPValidator())
        self.ip_ctrl.Bind(wx.EVT_TEXT, self.settings_save_ip)

        self.search_button = wx.Button(mainpanel, label='Search')
        self.search_button.Bind(wx.EVT_BUTTON, self.find_port)

        self.text_output = wx.TextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        sizer = wx.GridBagSizer()
        sizer.Add(self.info, pos=(0, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.device_label, pos=(1, 0), flag=wx.ALIGN_BOTTOM)
        sizer.Add(self.device_ctrl, pos=(2, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.community_label, pos=(3, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.community_ctrl, pos=(4, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.mac_label, pos=(5, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.mac_ctrl, pos=(6, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.ip_label, pos=(7, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.ip_ctrl, pos=(8, 0), flag=wx.ALIGN_TOP)
        sizer.Add(self.search_button, pos=(9, 0), flag=wx.ALIGN_TOP | wx.EXPAND)

        sizer.Add(self.text_output, pos=(0, 1), span=(11, 1), flag=wx.ALIGN_TOP | wx.EXPAND)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)
        mainpanel.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        x, y = sizer.GetSize()
        x += 500
        y += 150
        self.SetMinSize((x, y))
        self.SetSize((x, y))

        self.init_settings()

        # create a pubsub receiver
        Publisher.subscribe(self.update_log, "update")
        Publisher.subscribe(self.animate_search_button, "animate")

        self.Show(True)

    # ----------------------------------------------------------------------
    def animate_search_button(self, msg):
        self.search_button.SetLabel(msg)

    # ----------------------------------------------------------------------
    def update_log(self, msg):
        self.searchbuttonanimationthread.kill.set()
        self.text_output.AppendText(msg)
        self.separator()
        self.search_button.SetLabel("Search")
        self.search_button.Enable()

    # ----------------------------------------------------------------------
    def find_port(self, event):
        if len(self.mac_ctrl.GetValue().strip()) == 0 and len(self.ip_ctrl.GetValue().strip()) == 0:
            self.text_output.AppendText("Please enter MAC or IP\n")
            self.separator()
            return

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

        self.getportthread = GetPortThread(device=device, community=community, mac=mac, ip=ip)
        self.getportthread.daemon = True
        self.getportthread.start()
        self.search_button.Disable()
        self.searchbuttonanimationthread = SearchAnimation()
        self.searchbuttonanimationthread.daemon = True
        self.searchbuttonanimationthread.start()

    # ----------------------------------------------------------------------
    def settings_save_device(self, event):
        self.settings.setValue('device', self.device_ctrl.GetValue())

    # ----------------------------------------------------------------------
    def settings_save_mac(self, event):
        self.settings.setValue('mac', self.mac_ctrl.GetValue())

    # ----------------------------------------------------------------------
    def settings_save_community(self, event):
        self.settings.setValue('community', self.community_ctrl.GetValue())

    # ----------------------------------------------------------------------
    def settings_save_ip(self, event):
        self.settings.setValue('ip', self.ip_ctrl.GetValue())

    # ----------------------------------------------------------------------
    def init_settings(self):
        self.settings = YamlConfig(self.configfile)
        if not self.settings.value('device'):
            self.settings.setValue('device', '192.168.1.1')
        if not self.settings.value('community'):
            self.settings.setValue('community', 'public')
        ''' It's about default MAC and IP, but it's not necessary
        if not self.settings.value('mac'):
            self.settings.setValue('mac', '00 00 00 00 00 00')
        if not self.settings.value('ip'):
            self.settings.setValue('ip', '1.2.3.4')
        '''
        self.device_ctrl.SetValue(self.settings.value('device'))
        self.community_ctrl.SetValue(self.settings.value('community'))
        ''' Loading MAC and IP from settings, check the lines above - it's not necessary too
        self.mac_ctrl.SetValue(self.settings.value('mac'))
        self.ip_ctrl.SetValue(self.settings.value('ip'))
        '''

    # ----------------------------------------------------------------------
    def separator(self):
        self.text_output.AppendText("\n=======================\n\n")


class MainApp(wx.App):

    # ----------------------------------------------------------------------
    def OnInit(self):
        appname = "GetPortWX"
        ver = "1.0"
        title = '{n} (v.{v})'.format(n=appname, v=ver)
        appdatadir = AppDirs(appname)
        configfile = appdatadir.get_file('settings.yaml')
        self.frame = MainWindow(None, title, configfile)
        return True


if __name__ == "__main__":
    app = MainApp(0)
    app.MainLoop()
