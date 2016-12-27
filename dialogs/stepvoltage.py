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


class StepVoltage(wx.Dialog):

    def __init__(self, parent, instruments, variables):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Step Voltage")
        
        self._variables = variables
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        
        lbl_psu = wx.StaticText(panel, label="Power Supply:")        
        choices = instruments
        self.cbox_psu = wx.ComboBox(panel, choices=choices)
        self.cbox_psu.Bind(wx.EVT_COMBOBOX, self.OnPsuSelected)
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
        lbl_step_delay = wx.StaticText(panel, label="Delay before Increment/decrement (ms):")
        self.spin_step_delay = wx.SpinCtrl(panel, max=59, min=0, size=(50, -1))
        self.spin_step_delay2 = wx.SpinCtrl(panel, max=59, min=0, size=(50, -1))
        self.lbl_step_delay = wx.StaticText(panel, label="0.0s")
        self.spin_step_delay.Bind(wx.EVT_SPINCTRL, self.OnSpinStepDelay)
        self.spin_step_delay2.Bind(wx.EVT_SPINCTRL, self.OnSpinStepDelay)        
        grid.Add(lbl_step_delay, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_step_delay, pos=(row,1), flag=wx.ALL, border=5)
        grid.Add(self.spin_step_delay2, pos=(row,2), flag=wx.ALL, border=5)
        grid.Add(self.lbl_step_delay, pos=(row,3), flag=wx.ALL, border=5)
        
        row += 1
        lbl_repeat = wx.StaticText(panel, label="Repeat:")
        spin_repeat = wx.SpinCtrl(panel, max=999, min=0, size=(50, -1))
        grid.Add(lbl_repeat, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(spin_repeat, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
                  
        row += 1
        lbl_local = wx.StaticText(panel, label="Local Name:")
        default = defaultname = "stepvolt"
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
        
        # row += 1
        # self.lbl_error = wx.StaticText(panel, label="")
        # grid.Add(self.lbl_error, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        # if self.cbox_psu.GetSelection() == -1:
            # self.lbl_error.SetLabel("*Cannot add this step unless a power supply is selected")
        
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 0)
        sbox_sizer.AddSpacer(10)
        
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
        # self.SetSize((w, h*1.5))
        # self.SetMinSize((w, h*1.5))
        
        # self.SetMaxSize(sizer.Fit(self))
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass
            
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)    
    
    def OnPsuSelected(self, event):
        pass
        # self.btn_add.Enable()
        # self.lbl_error.SetLabel("")
    
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
        
    def OnSpinStep(self, event=None):
        v0 = self.spin_step.GetValue()
        v1 = self.spin_step2.GetValue()
        
        label = str(v0) + "." + str(v1) + "v"
        self.lbl_step2.SetLabel(label)
  
    def OnSpinStepDelay(self, event=None):
        s0 = self.spin_step_delay.GetValue()
        s1 = self.spin_step_delay2.GetValue()
        
        label = str(s0) + "." + str(s1) + "s"
        self.lbl_step_delay.SetLabel(label)
        
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
        self.lbl_step_delay.SetLabel(param_dict["delay"])
        self.lbl_step2.SetLabel(param_dict["step"])
        self.lbl_voltage.SetLabel(param_dict["v1"])
        self.lbl_voltage2.SetLabel(param_dict["v0"])
        
        #increment delay        
        spin1, spin2 = param_dict["delay"][:-1].split(".")
        
        self.spin_step_delay.SetValue(spin1)
        self.spin_step_delay.SetValue(spin2)
        
        #initial voltage
        spin1, spin2 = param_dict["v0"][:-1].split(".")
        
        self.spin_initial.SetValue(spin1)
        self.spin_initial2.SetValue(spin2)
        
        #final voltage 
        spin1, spin2 = param_dict["v1"][:-1].split(".")
        
        self.spin_final.SetValue(spin1)
        self.spin_final2.SetValue(spin2)
        
        #increment set
        spin1, spin2 = param_dict["step"][:-1].split(".")
        
        self.spin_step.SetValue(spin1)
        self.spin_step2.SetValue(spin2)
        
        #
        self.text_local.SetValue(data["local"])
        self.text_global.SetValue(data["global"])
        
    def GetValue(self):
    
        data = [("psu", self.cbox_psu.GetValue()),
                ("v0", self.lbl_voltage.GetLabel()),
                ("v1", self.lbl_voltage2.GetLabel()),
                ("step", self.lbl_step2.GetLabel()),
                ("delay", self.lbl_step_delay.GetLabel())]
        data = {"action":"Step Voltage", 
                "parameters":str(data)}
      
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