#!/usr/bin/env python3

import wx
import sys
import json
from twitchbot import TwitchBot
import subprocess
import sys
from wx.lib.agw.hyperlink import HyperLinkCtrl
import threading
import queue
import time

class Example(wx.Frame):

    SAVE = 1
    QUIT = 2
    
    def __init__(self, settings, *args, **kwargs):
        self.username = settings['twitch_username']
        self.channel = settings['twitch_channel']
        self.oauth = settings['oauth']
        self.lang = settings['lang']
        self.clientid = settings['clientid']
        self.clientsecret = settings['clientsecret']
        # Languages
        self.langBoxes = {}
        # GUI
        super(Example, self).__init__(*args, **kwargs)
        self.initMenu()
        self.initPanel()
        # Idle Bot
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        # Twitch
        self.bot = None

    def initMenu(self):
        menu = wx.MenuBar()
        fileMenu = wx.Menu()
        saveItem = fileMenu.Append(wx.ID_ANY, '&Save', 'Save Application')
        fileItem = fileMenu.Append(wx.ID_EXIT, '&Quit', 'Quit Application')
        menu.Append(fileMenu, '&File')
        self.SetMenuBar(menu)
        self.Bind(wx.EVT_MENU, self.Save, saveItem)
        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

    def initPanel(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        # Top
        toppan = wx.Panel(panel)
        toppan.SetBackgroundColour("#eedddd")
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        # Twitch Username
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(toppan, label="BOT Twitch Username"); hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.UserName = wx.TextCtrl(toppan); self.UserName.SetValue(self.username); hbox1.Add(self.UserName, proportion=1)
        vbox1.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        # OAuth
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(toppan, label="BOT OAuth                       "); hbox3.Add(st3, flag=wx.RIGHT, border=10)
        self.OAuth = wx.TextCtrl(toppan, style=wx.TE_PASSWORD); self.OAuth.SetValue(self.oauth); hbox3.Add(self.OAuth, proportion=1)
        vbox1.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        # Twitch Channel
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(toppan, label="STREAMING Twitch Channel "); hbox2.Add(st2, flag=wx.RIGHT, border=8)
        self.Channel = wx.TextCtrl(toppan); self.Channel.SetValue(self.channel); hbox2.Add(self.Channel, proportion=1)
        vbox1.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        # Start Button
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        bt1 = wx.Button(toppan, label="Start")
        bt1.Bind(wx.EVT_BUTTON, self.Start) 
        hbox3.Add(bt1)
        bt2 = wx.Button(toppan, label="Stop")
        bt2.Bind(wx.EVT_BUTTON, self.Stop) 
        hbox3.Add(bt2)
        vbox1.Add(hbox3)

        # Language Picker
        hs = wx.BoxSizer(wx.HORIZONTAL)
        rb1 = wx.BoxSizer(wx.VERTICAL)
        txt11 = wx.StaticText(toppan, label="English->"); #txt11.SetLabelMarkup("<big>English-></big>")
        rbt1 = wx.CheckBox(toppan, label="Korean")
        rbt2 = wx.CheckBox(toppan, label="Japanese")
        rbt3 = wx.CheckBox(toppan, label="Chinese")
        [rb1.Add(r) for r in [txt11, rbt1, rbt2, rbt3]]
        hs.Add(rb1, flag=wx.ALL, border=10)
        self.langBoxes[rbt1] = ["en", "ko"]
        self.langBoxes[rbt2] = ["en", "ja"]
        self.langBoxes[rbt3] = ["en", "zh-CN"]

        rb1 = wx.BoxSizer(wx.VERTICAL)
        txt11 = wx.StaticText(toppan, label="Korean->"); #txt11.SetLabelMarkup("<big>Korean-></big>")
        rbt1 = wx.CheckBox(toppan, label="English")
        rbt2 = wx.CheckBox(toppan, label="Japanese")
        rbt3 = wx.CheckBox(toppan, label="Chinese")
        [rb1.Add(r) for r in [txt11, rbt1, rbt2, rbt3]]
        hs.Add(rb1, flag=wx.ALL, border=10)
        self.langBoxes[rbt1] = ["ko", "en"]
        self.langBoxes[rbt2] = ["ko", "ja"]
        self.langBoxes[rbt3] = ["ko", "zh-CN"]
        
        rb1 = wx.BoxSizer(wx.VERTICAL)
        txt11 = wx.StaticText(toppan, label="Japanese->"); #txt11.SetLabelMarkup("<big>Japanese-></big>")
        rbt1 = wx.CheckBox(toppan, label="English")
        rbt2 = wx.CheckBox(toppan, label="Korean")
        rbt3 = wx.CheckBox(toppan, label="Chinese")
        [rb1.Add(r) for r in [txt11, rbt1, rbt2, rbt3]]
        hs.Add(rb1, flag=wx.ALL, border=10)
        self.langBoxes[rbt1] = ["ja", "en"]
        self.langBoxes[rbt2] = ["ja", "ko"]
        self.langBoxes[rbt3] = ["ja", "zh-CN"]
        
        rb1 = wx.BoxSizer(wx.VERTICAL)
        txt11 = wx.StaticText(toppan, label="Chinese->"); #txt11.SetLabelMarkup("<big>Chinese-></big>")
        rbt1 = wx.CheckBox(toppan, label="English")
        rbt2 = wx.CheckBox(toppan, label="Korean")
        rbt3 = wx.CheckBox(toppan, label="Japanese")
        [rb1.Add(r) for r in [txt11, rbt1, rbt2, rbt3]]
        hs.Add(rb1, flag=wx.ALL, border=10)
        self.langBoxes[rbt1] = ["zh-CN", "en"]
        self.langBoxes[rbt2] = ["zh-CN", "ko"]
        self.langBoxes[rbt3] = ["zh-CN", "ja"]

        vbox1.Add(hs)

        for k, v in self.langBoxes.items():
            if v in self.lang:
                k.SetValue(True)
            else:
                k.SetValue(False)
            k.Bind(wx.EVT_CHECKBOX, self.UpdateLang, k)
        
        # For Hongmin
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(14, wx.SWISS, wx.ITALIC, wx.NORMAL, True)
        st2 = HyperLinkCtrl(toppan, label="Made for yasumi57", URL="https://www.twitch.tv/yasumi57"); st2.SetFont(font); hbox2.Add(st2, flag=wx.EXPAND|wx.RIGHT, border=10)
        vbox1.Add(hbox2, flag=wx.EXPAND|wx.ALL, border=10)
        # Finished
        toppan.SetSizer(vbox1)
        # Bottom
        botpan = wx.Panel(panel)
        botpan.SetBackgroundColour("#000000")
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.Log = wx.TextCtrl(botpan, wx.ID_ANY, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        self.Log.SetBackgroundColour("#444444")
        self.Log.SetForegroundColour("#efefef")
        hbox4.Add(self.Log, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        botpan.SetSizer(hbox4)
        # Add them together
        vbox.Add(toppan, wx.ID_ANY, wx.EXPAND | wx.ALL, 10)
        vbox.Add(botpan, wx.ID_ANY, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(vbox)
        

    def OnQuit(self, e):
        self.Save(e)
        self.Close()

    def Save(self, e):
        json.dump(
            {
                'twitch_username' : self.UserName.GetValue(),
                'twitch_channel' : self.Channel.GetValue(),
                'oauth' : self.OAuth.GetValue(),
                'lang' : self.lang,
                'clientsecret' : self.clientsecret,
                'clientid' : self.clientid
            },
            open('settings.json', 'w'))

    def Start(self, e):
        self.queue = queue.Queue()
        def runbot(*args, **kwargs):
            bot = TwitchBot(*args, **kwargs)
            bot.start()
        self.bot = threading.Thread(
            target=runbot,
            kwargs={
                "username":self.UserName.GetValue(),
                "channel":self.Channel.GetValue(),
                "oauth":self.OAuth.GetValue(),
                "lang": self.lang,
                "clientid":self.clientid,
                "queue":self.queue})
        self.bot.daemon = True
        self.bot.start()
        # self.bot = subprocess.Popen([
        #     sys.executable, 'twitchbot.py',
        #     '--username', self.UserName.GetValue(),
        #     '--channel', self.Channel.GetValue(),
        #     '--oauth', self.OAuth.GetValue(),
        #     '--clientid', self.clientid,
        #     '--lang', *[f"{f},{t}" for f, t in self.lang]
        # ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # pipe_no_wait(self.bot.stdout.fileno())
        # pipe_no_wait(self.bot.stderr.fileno())
        self.Log.WriteText("SYS\tStarting TwitchBot\n")

    def Stop(self, e):
        self.Log.WriteText("SYS\tShutting down TwitchBot\n")
        self.bot.terminate()
        self.bot = None

    def UpdateLang(self, e):
        self.lang = []
        for k, v in self.langBoxes.items():
            if k.GetValue():
                self.lang.append(v)

    def OnIdle(self, e):
        if self.bot:
            p = False # self.bot.poll()
            if p:
                self.bot = None
                self.Log.WriteText("SYS\tTwitchBot Ended\n")
                return
            try:
                nxt = self.queue.get(False)
                self.Log.WriteText("BOT\t"+nxt+'\n')
            except queue.Empty:
                pass
            time.sleep(0.2)
            e.RequestMore()

# From https://chase-seibert.github.io/blog/2012/11/16/python-subprocess-asynchronous-read-stdout.html
import os

if os.name != "nt":
  import fcntl
  def pipe_no_wait(*args):
      return True
  def non_block_read(output):
    ''' even in a thread, a normal read with block until the buffer is full '''
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except:
        return ''
else:
    # https://gist.github.com/techtonik/48c2561f38f729a15b7b
    import msvcrt
    import os

    from ctypes import windll, byref, wintypes, GetLastError, WinError
    from ctypes.wintypes import HANDLE, DWORD, BOOL, PDWORD

    LPDWORD = PDWORD # POINTER(DWORD)

    PIPE_NOWAIT = wintypes.DWORD(0x00000001)

    ERROR_NO_DATA = 232

    def pipe_no_wait(pipefd):
      """ pipefd is a integer as returned by os.pipe """

      SetNamedPipeHandleState = windll.kernel32.SetNamedPipeHandleState
      SetNamedPipeHandleState.argtypes = [HANDLE, LPDWORD, LPDWORD, LPDWORD]
      SetNamedPipeHandleState.restype = BOOL

      h = msvcrt.get_osfhandle(pipefd)

      res = windll.kernel32.SetNamedPipeHandleState(h, byref(PIPE_NOWAIT), None, None)
      if res == 0:
          print(WinError())
          return False
      return True
    def non_block_read(output):
     try:
       return output.read()
     except:
       return ''

def main():
    settings = json.load(open('settings.json', 'r'))
    app = wx.App()
    frame = Example(settings, None, title='Simple App')
    frame.SetDimensions(50,50,600,1000)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
