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

import logging
import sys
import time
import wx
import theme
import base


class SetVoltage(wx.Dialog):

    def __init__(self, parent, instruments):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Set Voltage")
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        
        lbl_psu = wx.StaticText(panel, label="Power Supply:")
        choices = ["Choose on execution"]
        choices.extend(instruments)
        self.cbox_psu = wx.ComboBox(panel, choices=choices)
        # self.cbox_psu.Bind(wx.EVT_COMBOBOX, self.OnPsuSelected)
        grid.Add(lbl_psu, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.cbox_psu, pos=(row,1), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)
        row += 1
        text_voltage = wx.StaticText(panel, label="Set Voltage:")
        self.spin_voltage = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_voltage2 = wx.SpinCtrl(panel, max=99, min=0, size=(50, -1))
        self.spin_voltage.Bind(wx.EVT_SPINCTRL, self.OnSpinVoltage)
        self.spin_voltage2.Bind(wx.EVT_SPINCTRL, self.OnSpinVoltage)
        self.lbl_voltage = wx.StaticText(panel, label="0.0v")
        grid.Add(text_voltage, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_voltage, pos=(row,1), flag=wx.ALL, border=5)
        grid.Add(self.spin_voltage2, pos=(row,2), flag=wx.ALL, border=5)
        grid.Add(self.lbl_voltage, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)
        
        
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 0)
        sbox_sizer.AddSpacer(10)
        
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add = wx.Button(panel, label="Add", id=wx.ID_OK)
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btn_add, 0, wx.ALL|wx.EXPAND, 5)
                        
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
        
    def OnSpinVoltage(self, event=None):
        v0 = self.spin_voltage.GetValue()
        v1 = self.spin_voltage2.GetValue()
        
        label = str(v0) + "." + str(v1) + "v"
        self.lbl_voltage.SetLabel(label)
      
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Add":            
            self.EndModal(id)

     
    def SetValue(self, data):
        params = data["parameters"]
        params = "), " + params[1:-1] + ", (" #so we can split it easier
        
        param_dict = {}
        
        params = params.split("), (")
        
        for param in params:            
            param = param[1: -1] 
            if param == "":
                continue
            key, value = param.split("', '")
            param_dict[key] = value
        
        self.cbox_psu.SetValue(param_dict["psu"])
        self.lbl_voltage.SetLabel(param_dict["v0"])
        
        
        spin1, spin2 = param_dict["v0"][:-1].split(".")
        self.spin_voltage.SetValue(spin1)
        self.spin_voltage2.SetValue(spin2)
        
    def GetValue(self):
    
        psu = self.cbox_psu.GetValue()
        if psu != "":
            for char in psu:
                if char.isdigit() or char.isalpha():
                    continue
                psu = psu.replace(char, "_")    
                
        data = [("psu", psu),
                ("v0", self.lbl_voltage.GetLabel())]
        data = {"action":"Set Voltage",
                "parameters":str(data),}
        
        return data        