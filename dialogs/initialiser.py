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


class InitialiseSequence(wx.Dialog):

    def __init__(self, parent):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Initialise Sequence...")
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        for label in ["From", "To", "Name", "Author", "Tester", "Company", "Description", "Information"]:
            lbl = wx.StaticText(panel, label=label+":")
            self.textctrl = wx.TextCtrl(panel, value="")
            grid.Add(lbl, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
            grid.Add(self.textctrl, pos=(row,1), span=(0,5), flag=wx.ALL|wx.EXPAND, border=5)            
            row += 1
        grid.AddGrowableCol(1)
        
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 0)
        sbox_sizer.AddSpacer(10)
        
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        btn_confirm = wx.Button(panel, label="Execute", id=wx.ID_OK)
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
        
    def OnSpinInitial(self, event=None):
        v0 = self.spin_initial.GetValue()
        v1 = self.spin_initial2.GetValue()
        
        label = str(v0) + "." + str(v1) + "v"
        self.lbl_voltage.SetLabel(label)
        
    def OnSpinFinal(self, event=None):
        v0 = self.spin_final.GetValue()
        v1 = self.spin_final2.GetValue()
        
        label = str(v0) + "." + str(v1) + "v"
        self.lbl_voltage2.SetLabel(label)
        
    def OnSpinVarA(self, event):
        v0 = self.spin_var_a.GetValue()
        v1 = self.spin_var_a2.GetValue()
        
        unit = self.lbl_var_a.GetLabel()[-1]        
        label = str(v0) + "." + str(v1) + unit
        self.lbl_var_a.SetLabel(label)
        
    def OnSpinVarB(self, event):
        v0 = self.spin_var_b.GetValue()
        v1 = self.spin_var_b2.GetValue()
        
        unit = self.lbl_var_b.GetLabel()[-1]
        label = str(v0) + "." + str(v1) + unit
        self.lbl_var_b.SetLabel(label)
        
    def OnSpinStep(self, event=None):
        v0 = self.spin_step.GetValue()
        v1 = self.spin_step2.GetValue()
        
        label = str(v0) + "." + str(v1) + "v"
        self.lbl_step2.SetLabel(label)
  
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Confirm":            
            self.EndModal(id)

    def GetValue(self):
    
        data = [("psu", self.cbox_psu.GetValue()),
                ("v0", self.lbl_voltage.GetLabel()[1:-1]),
                ("v1", self.lbl_voltage2.GetLabel()[1:-1]),
                ("step", self.lbl_step2.GetLabel()[3:-1]),
                ("delay", self.spin_step_delay.GetValue())]
        data = "Step Voltage >> " + str(data)
        
        return data        