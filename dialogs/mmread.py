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


import json
import logging
import serial
import serialfunctions as sf
import sys
import time
import wx
import theme
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
import base
# from wx.lib.agw import spinctrl

OHM = "Ω"
MULTIMETER_SCPI = [(),
                   (),
                   (),
                   (),]
                   
INSTRUCTIONS = [("DMM", "Voltage", "Read Voltage"),
                ("INS", "General", "Reset Instrument"),
                ("INS", "General", "Power Off Instrument"),
                ("PSU", "Current", "Set Current Limit"),
                ("PSU", "Voltage", "Set Voltage"),                
                ("PSU", "Voltage", "Step Voltage"),
                ("SBC", "CAN", "Send Message")]


#------------------------------------------------#
# add action to sequence pop-up frames
#------------------------------------------------#

class AddStepVoltage(wx.Dialog):

    def __init__(self, parent):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Step Voltage")
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="Test Setup: Step Voltage")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        row += 1 #let's start at 1, to give some space
        
        lbl_psu = wx.StaticText(panel, label="Power Supply:")
        choices = []
        self.cbox_psu = wx.ComboBox(panel, choices=choices)
        grid.Add(lbl_psu, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.cbox_psu, pos=(row,1), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)
        row += 1
        lbl_initial = wx.StaticText(panel, label="Initial Voltage:")
        self.spin_initial = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_initial2 = wx.SpinCtrl(panel, max=99, min=0, size=(50, -1))
        self.spin_initial.Bind(wx.EVT_SPINCTRL, self.OnSpinInitial)
        self.spin_initial2.Bind(wx.EVT_SPINCTRL, self.OnSpinInitial)
        self.lbl_voltage = wx.StaticText(panel, label="0.0v")
        grid.Add(lbl_initial, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_initial, pos=(row,1), flag=wx.ALL, border=5)
        grid.Add(self.spin_initial2, pos=(row,2), flag=wx.ALL, border=5)
        grid.Add(self.lbl_voltage, pos=(row,3), flag=wx.ALL, border=5)
        
        row += 1
        lbl_final = wx.StaticText(panel, label="Final Voltage (Limit):")
        self.spin_final = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_final2 = wx.SpinCtrl(panel, max=99, min=0, size=(50, -1))
        self.spin_final.Bind(wx.EVT_SPINCTRL, self.OnSpinFinal)
        self.spin_final2.Bind(wx.EVT_SPINCTRL, self.OnSpinFinal)
        self.lbl_voltage2 = wx.StaticText(panel, label="0.0v")
        grid.Add(lbl_final, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_final, pos=(row,1), flag=wx.ALL, border=5)
        grid.Add(self.spin_final2, pos=(row,2), flag=wx.ALL, border=5)
        grid.Add(self.lbl_voltage2, pos=(row,3), flag=wx.ALL, border=5)
        
        row += 1
        lbl_step = wx.StaticText(panel, label="Voltage Increment/Decrement:")
        self.spin_step = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_step2 = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_step.Bind(wx.EVT_SPINCTRL, self.OnSpinStep)
        self.spin_step2.Bind(wx.EVT_SPINCTRL, self.OnSpinStep)
        self.lbl_step2 = wx.StaticText(panel, label="0.0v")
        grid.Add(lbl_step, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_step, pos=(row,1), flag=wx.ALL, border=5)
        grid.Add(self.spin_step2, pos=(row,2), flag=wx.ALL, border=5)
        grid.Add(self.lbl_step2, pos=(row,3), flag=wx.ALL, border=5)
        
        row += 1
        lbl_step_delay = wx.StaticText(panel, label="Increment/decrement delay (ms):")
        self.spin_step_delay = wx.SpinCtrl(panel, max=0, min=0, size=(50, -1))
        grid.Add(lbl_step_delay, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_step_delay, pos=(row,1), span=(0,2), flag=wx.ALL, border=5)
        
        row += 1
        lbl_repeat = wx.StaticText(panel, label="Repeat:")
        spin_repeat = wx.SpinCtrl(panel, max=999, min=0, size=(50, -1))
        grid.Add(lbl_repeat, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(spin_repeat, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        # hsizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_read = wx.StaticText(panel, label="Read Voltage:")
        choices = ["Choose on execution"]
        self.cbox_read = wx.ComboBox(panel, choices=choices, value=choices[0])
        grid.Add(lbl_read, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.cbox_read, pos=(row,1), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)
                
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 0)
        sbox_sizer.AddSpacer(20)
        
        #rhs staticboxsizer
        sbox2 = wx.StaticBox(panel, label="Pass/Fail Condition")
        sbox_sizer2 = wx.StaticBoxSizer(sbox2, wx.HORIZONTAL)
                
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddSpacer(20)
        
        grid2 = wx.GridBagSizer(2,2)
        row = 0           
        vars = ["V - Voltage reading (V)",
                "I - Current reading (A)",
                "R - Resistance reading (%s)" %OHM]
        conditions = ["in range",
                    "not in range",
                    "in % range",
                    "not in % range",
                    "> (greater than)",
                    ">= (greater than/equal to)",
                    "< (less than)",
                    "<= (less than/equal to)"]        
        self.cbox_var = wx.ComboBox(panel, choices=vars, name="reading", style=wx.CB_READONLY)
        self.cbox_var.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
        self.cbox_var.SetSelection(0)
        self.cbox_conditions = wx.ComboBox(panel, choices=conditions, name="condition", style=wx.CB_READONLY)  
        self.cbox_conditions.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
        self.cbox_conditions.SetSelection(0)
        
        grid2.Add(self.cbox_var, pos=(row,1), span=(0, 0), flag=wx.ALL|wx.EXPAND, border=5)
        grid2.Add(self.cbox_conditions, pos=(row,2), span=(0, 0), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1   
        lbl_testvar_a = wx.StaticText(panel, label="Value 1:")
        self.spin_var_a = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_var_a.Bind(wx.EVT_SPINCTRL, self.OnSpinVarA)
        self.spin_var_a2 = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_var_a2.Bind(wx.EVT_SPINCTRL, self.OnSpinVarA)
        self.lbl_var_a = wx.StaticText(panel, label="0.0V")        
        
        grid2.Add(lbl_testvar_a, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid2.Add(self.spin_var_a, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)        
        grid2.Add(self.spin_var_a2, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid2.Add(self.lbl_var_a, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)          
        
        row += 1   
        lbl_testvar_b = wx.StaticText(panel, label="Value 2:")
        self.spin_var_b = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_var_b.Bind(wx.EVT_SPINCTRL, self.OnSpinVarB)
        self.spin_var_b2 = wx.SpinCtrl(panel, max=30, min=0, size=(50, -1))
        self.spin_var_b2.Bind(wx.EVT_SPINCTRL, self.OnSpinVarB)
        self.lbl_var_b = wx.StaticText(panel, label="0.0V")        
        
        grid2.Add(lbl_testvar_b, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid2.Add(self.spin_var_b, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)        
        grid2.Add(self.spin_var_b2, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)   
        grid2.Add(self.lbl_var_b, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)   
        
        grid2.AddGrowableCol(0)
        vsizer.Add(grid2, 0, wx.ALL|wx.EXPAND, 5)
        
        vsizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 5)
        
        hsizer_radios = wx.BoxSizer(wx.HORIZONTAL)   
        lbl_fail = wx.StaticText(panel, label="On Test Failure:")
        hsizer_radios.Add(lbl_fail, 0, wx.ALL|wx.EXPAND, 5)
        for label in ["Continue", "Stop", "Ask on failure"]:        
            radio = wx.RadioButton(panel, label=label)
            radio.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
            hsizer_radios.Add(radio, 0, wx.ALL|wx.EXPAND, 5)        
        vsizer.Add(hsizer_radios, 0, wx.ALL|wx.EXPAND, 5)  
        
        
        
        sbox_sizer2.Add(vsizer, 1, wx.ALL|wx.EXPAND, 5)
        
        # add static boxes to hsizer
        hsizer.Add(sbox_sizer, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(sbox_sizer2, 0, wx.ALL|wx.EXPAND, 5)
        
        #-----
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        btn_confirm = wx.Button(panel, label="Confirm")
        btn_confirm.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer2.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer2.Add(btn_confirm, 0, wx.ALL|wx.EXPAND, 5)
                        
        #add to main sizer
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer2, 0, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizer(sizer)  
        
        w, h = sizer.Fit(self)  
        # self.SetSize((w, h*1.5))
        # self.SetMinSize((w, h*1.5))
        
        # self.SetMaxSize(sizer.Fit(self))
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass
            
        # self.Bind(wx.EVT_KEY)    
    
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
    
    def OnComboBox(self, event):
        e = event.GetEventObject()
        name = e.GetName()
        value = e.GetStringSelection()               

        if name == "reading":
            if "Voltage" in value:
                unit = "V"
            elif "Current" in value:
                unit = "A"
            elif "Resistance" in value:
                unit = OHM
                
            #change unit accordingly
            label = self.lbl_var_a.GetLabel()
            if label[-1] == "%":
                return
            label = label[:-1] + unit
            self.lbl_var_a.SetLabel(label)
            
            label = self.lbl_var_b.GetLabel()
            label = label[:-1] + unit
            self.lbl_var_b.SetLabel(label)
                
        elif name == "condition":            
            if "%" in value:
                self.spin_var_b.Disable()
                self.spin_var_b2.Disable()
                
                label = self.lbl_var_a.GetLabel()
                if not label.endswith("%"):                     
                    label = label[:-1] + "%"                
                self.lbl_var_a.SetLabel(label)
                
                label = self.lbl_var_b.GetLabel()
                if not label.endswith("%"):                     
                    label = label[:-1] + "%"                
                self.lbl_var_b.SetLabel(label)
                return                
            elif value in ["in range","not in range"]:
                self.spin_var_b.Enable()
                self.spin_var_b2.Enable()
            else:
                self.spin_var_b.Disable()
                self.spin_var_b2.Disable()
            
            label = self.lbl_var_a.GetLabel()
            if label.endswith("%"):                    
                value = self.cbox_var.GetStringSelection()
                if "Voltage" in value:
                    unit = "V"
                elif "Current" in value:
                    unit = "A"
                elif "Resistance" in value:
                    unit = OHM
                                      
                label = label[:-1] + unit
                self.lbl_var_a.SetLabel(label)
                
                label = self.lbl_var_b.GetLabel()
                label = label[:-1] + unit
                self.lbl_var_b.SetLabel(label)
    
    def OnRadioButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        self.on_failure = label
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Add":
            test = self.cbox_conditions.GetValue()
            test += self.lbl_var_a.GetLabel() 
            test += self.lbl_var_b.GetLabel()
            failure = self.on_failure
            self.list_passfail.Append([test,failure])
            
        if label == "Cancel":
            self.EndModal(id)
            
        elif label == "Confirm":
            data = {"action": "Step Voltage",
                    "psu":self.cbox_psu.GetValue(),
                    "v0":self.lbl_voltage.GetLabel()[1:-1],
                    "v1":self.lbl_voltage2.GetLabel()[1:-1],
                    "step":self.lbl_step2.GetLabel()[3:-1],
                    "delay":self.spin_step_delay.GetValue(),
                    "repeat":self.cbox_read.GetValue(),
                    "read":self.cbox_read.GetValue()}
            self.EndModal(id)

            
class AddSetVoltage(wx.Frame):

    def __init__(self):
    
        wx.Frame.__init__(self,
                          parent=None,
                          title="Set Voltage")
                          