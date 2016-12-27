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


class AddFunction(wx.Dialog):

    def __init__(self, parent):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Add New Function")
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        
        lbl_function = wx.StaticText(panel, label="Function Name:", style=wx.TE_PROCESS_ENTER)
        self.text_function = wx.TextCtrl(panel)
        self.text_function.Bind(wx.EVT_TEXT_ENTER, self.OnFunctionEnter)
        self.text_function.Bind(wx.EVT_TEXT, self.OnFunctionChange)
        
        grid.Add(lbl_function, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.text_function, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)
        row += 1
      
        sbox_sizer.AddSpacer(10)
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 2)
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add = wx.Button(panel, label="Add", id=wx.ID_OK)
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add.Disable()
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
            
    def OnFunctionChange(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        # e.SetValue(value.replace(" ", ""))
        
        if e.GetValue() == "":
            self.btn_add.Disable()
        elif e.GetValue().lower() in ["setup","main"]:
            self.btn_add.Disable()
        else:   
            self.btn_add.Enable()
   
    def OnFunctionEnter(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        if value == "":
            return                  
       
        self.EndModal(id)
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Add":            
            self.EndModal(id)
    
    def SetValue(self, name): 
        self.text_function.SetValue(name)
    
    def GetValue(self): 

        function = self.text_function.GetValue()
        if function != "":
            for char in function:
                if char.isdigit() or char.isalpha():
                    continue
                function = function.replace(char, "_")                 
            
        data = function
        
        return data