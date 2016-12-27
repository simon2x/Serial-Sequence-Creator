"""
Description: 
Requirements: pySerial, wxPython Phoenix

glossary and of other descriptions:

DMM - digital multimeter
PSU - power supply
SBC - single board computer

INS - general instrument commands

GEN - general sequence instructions

"""

import wx
import theme
import base
# from wx.lib.agw import spinctrl


class AddDelay(wx.Dialog):

    def __init__(self, parent):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Add Delay")
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        
        lbl_delay = wx.StaticText(panel, label="Add custom delay:")
        self.spin_delay = wx.SpinCtrl(panel, max=10, min=0, size=(50, -1))
        self.spin_delay2 = wx.SpinCtrl(panel, max=59, min=0, size=(50, -1))
        self.spin_delay.Bind(wx.EVT_SPINCTRL, self.OnSpinDelay)
        self.spin_delay2.Bind(wx.EVT_SPINCTRL, self.OnSpinDelay)
        self.lbl_delay = wx.StaticText(panel, label="0.0s")
        grid.Add(lbl_delay, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_delay, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_delay2, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.lbl_delay, pos=(row,3), flag=wx.ALL|wx.ALIGN_BOTTOM, border=5)
        
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 0)
        sbox_sizer.AddSpacer(10)
        
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        btn_confirm = wx.Button(panel, label="Confirm", id=wx.ID_OK)
        btn_confirm.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(btn_confirm, 0, wx.ALL|wx.EXPAND, 5)
                        
        #add to main sizer
        sizer.Add(sbox_sizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizer(sizer)  
        
        w, h = sizer.Fit(self)  
        # self.SetSize((w, h*1.5))
        # self.SetMinSize((w, h*1.5))
        
        # self.SetMaxSize(sizer.Fit(self))
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass
            
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)    
    
    def OnKeyUp(self, event):
        key = event.GetKeyCode()  
        print(event)    
        if key == wx.KEY_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        
    def OnSpinDelay(self, event=None):
        s0 = self.spin_delay.GetValue()
        s1 = self.spin_delay2.GetValue()
        
        label = str(s0) + "." + str(s1) + "s"
        self.lbl_delay.SetLabel(label)
     
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Confirm":            
            self.EndModal(id)

    def SetValue(self, data):    
        delay = data["parameters"]
            
        self.lbl_delay.SetLabel(delay)
        
        #increment delay        
        spin1, spin2 = delay[:-1].split(".")
        
        self.spin_delay.SetValue(spin1)
        self.spin_delay2.SetValue(spin2)
        
    def GetValue(self):
    
        data = {"action":"Delay", "parameters":str(self.lbl_delay.GetLabel())}
        
        return data        