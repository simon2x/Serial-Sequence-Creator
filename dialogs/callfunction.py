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


class CallFunction(wx.Dialog):

    def __init__(self, parent, functions, variables):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Add Function Call")
        
        self._variables = variables
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        
        lbl_function = wx.StaticText(panel, label="Function Name:")
        choices = functions
        self.cbox_function = wx.ComboBox(panel, choices=choices)
        # self.cbox_function.Bind(wx.EVT_COMBOBOX, self.OnFunctionSelection)
        
        grid.Add(lbl_function, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.cbox_function, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)
        row += 1
      
        row += 1
        lbl_local = wx.StaticText(panel, label="Local Name:")
        default = defaultname = "func"
        index = 1
        while defaultname in self._variables["locals"]:
            defaultname = default + str(index)
            index += 1        
        self.text_local = wx.TextCtrl(panel, value=defaultname)
        grid.Add(lbl_local, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.text_local, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lbl_global = wx.StaticText(panel, label="Global Name:")
        self.text_global = wx.TextCtrl(panel, value="")
        grid.Add(lbl_global, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.text_global, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        sbox_sizer.AddSpacer(10)
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 2)
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add = wx.Button(panel, label="Add", id=wx.ID_OK)
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        # self.btn_add.Disable()
        hsizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btn_add, 0, wx.ALL|wx.EXPAND, 5)
                        
        #add to main sizer
        sizer.Add(sbox_sizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizer(sizer)  
        
        w, h = sizer.Fit(self)
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass
            
    def OnFunctionSelection(self, event):
        self.btn_add.Enable()
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Add":            
            self.EndModal(id)

    def SetValue(self, data):
        parameters = data["parameters"]
        self.cbox_function.SetValue(parameters)
        
        #
        self.text_local.SetValue(data["local"])
        self.text_global.SetValue(data["global"])
        
    def GetValue(self):        
        data = {"parameters": self.cbox_function.GetValue(),
                "action": "Call Function"}
                
        local = self.text_local.GetValue()
        if local != "":
            for char in local:
                if char.isdigit() or char.isalpha():
                    continue
                local = local.replace(char, "_")     
            data["local"] = local
         
        glob = self.text_global.GetValue()
        if glob != "":
            for char in glob:
                if char.isdigit() or char.isalpha():
                    continue
                glob = glob.replace(char, "_")     
            data["global"] = glob
            
        return data