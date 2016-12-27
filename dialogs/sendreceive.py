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


class SendReceive(wx.Dialog):

    def __init__(self, parent, instruments, variables):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Send and Receive Message")
        
        self._variables = variables
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        
        ins_lbl = wx.StaticText(panel, label="Instruments:")
        choices = instruments
        choices.extend(instruments)
        self.cbox_ins = wx.ComboBox(panel, choices=choices)
        self.cbox_ins.Bind(wx.EVT_COMBOBOX, self.OnInstrumentSelect)
        grid.Add(ins_lbl, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.cbox_ins, pos=(row,1), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)
        
        row += 1
        lbl_send = wx.StaticText(panel, label="Send Command:")
        self.command = wx.TextCtrl(panel)       
        grid.Add(lbl_send, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.command, pos=(row,1), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lbl_delay = wx.StaticText(panel, label="Delay before send:")
        self.spin_delay = wx.SpinCtrl(panel, max=10, min=0, size=(50, -1))
        self.spin_delay2 = wx.SpinCtrl(panel, max=59, min=0, size=(50, -1))
        self.spin_delay.Bind(wx.EVT_SPINCTRL, self.OnSpinDelay)
        self.spin_delay2.Bind(wx.EVT_SPINCTRL, self.OnSpinDelay)
        self.lbl_delay = wx.StaticText(panel, label="0.0s")
        grid.Add(lbl_delay, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_delay, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_delay2, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.lbl_delay, pos=(row,3), flag=wx.ALL|wx.ALIGN_BOTTOM, border=5)
        
        row += 1
        lbl_local = wx.StaticText(panel, label="Local Name:")
        default = defaultname = "serial_read"
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
        
    def OnSpinDelay(self, event=None):
        s0 = self.spin_delay.GetValue()
        s1 = self.spin_delay2.GetValue()
        
        label = str(s0) + "." + str(s1) + "s"
        self.lbl_delay.SetLabel(label)
    
    def OnInstrumentSelect(self, event):
        e = event.GetEventObject()
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
        
        self.command.SetValue(param_dict["command"])
        self.cbox_ins.SetValue(param_dict["instrument"])
        self.lbl_delay.SetLabel(param_dict["delay"]+"s")
        spin1, spin2 = param_dict["delay"].split(".")
        self.spin_delay.SetValue(spin1)
        self.spin_delay2.SetValue(spin2)
        
        self.text_local.SetValue(data["local"])
        self.text_global.SetValue(data["global"])
        
    def GetValue(self):
    
        command = self.command.GetValue()
        command = command.replace("), (", "_")    
        
        instrument = self.cbox_ins.GetValue()
        instrument = instrument.replace("), (", "_")    
        
        data = [("command", command),
                ("instrument", instrument),
                ("delay", self.lbl_delay.GetLabel()[0:-1])]
        data = {"action": "Send and Receive Message",
                "parameters": str(data)}
                
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