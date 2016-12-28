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
import serialfunctions as sf
# from wx.lib.agw import spinctrl


class SetupInstruments(wx.Dialog):

    def __init__(self, parent, instrument_data, variables):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Setup Instruments")
        
        # sort data 
        self._instrument_data = instrument_data
        
        self._variables = variables
        
        self.serial_options = ["baudrate",
                               "port",
                               "bytesize",
                               "stopbits",
                               "flowcontrol",
                               "parity",
                               "timeout",
                               "idcmd",
                               "id",
                               "type"]
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        # row += 1 #let's start at 1, to give some space
        
        ins_lbl = wx.StaticText(panel, label="Instruments:")
        choices = [k for k in self._instrument_data.keys()]
        self.cbox_ins = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)    
        self.cbox_ins.Bind(wx.EVT_COMBOBOX, self.OnInstrumentSelection)
        grid.Add(ins_lbl, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.cbox_ins, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=2)
        grid.AddGrowableCol(1)
        
        self.serial_data = {}
        
        row += 1
        items = [("port", "Port", "COM1"),
                 ("baudrate", "Speed (baud)", "9600", ["110","300","600","1200","2400","4800","9600",
                                                       "14400","19200","28800","38400","56000","57600",
                                                       "115200","128000","153600","230400","256000",
                                                       "460800","921600"]),
                 ("bytesize", "Data bits", "8", [str(x) for x in range(5, 10)]),
                 ("stopbits", "Stop bits", "1", [str(x) for x in range(0, 3)]),
                 ("parity", "Parity", "None", ["None","Odd","Even","Mark","Space"]),
                 ("flowcontrol", "Flow control", "None", ["None","XON/XOFF","RTS/CTS","DSR/DTR"]),
                 ("timeout", "Timeout (s)", "1", [str(x) for x in range(1, 61, 1)])]
        
        
        name, label, default = items[0]
        lbl = wx.StaticText(panel, label=label)        
        self.serial_data[name] = wx.TextCtrl(panel, value=default)        
        grid.Add(lbl, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data[name], pos=(row, 1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=2)                
        row += 1
        
        for name, label, default, choices in items[1:]:            
            lbl = wx.StaticText(panel, label=label)        
            self.serial_data[name] = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
            self.serial_data[name].SetValue(default)
            grid.Add(lbl, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
            grid.Add(self.serial_data[name], pos=(row, 1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=2)            
            row += 1
        
        # add a separator
        row += 1        
        grid.Add(wx.StaticLine(panel), pos=(row, 0), span=(0,3), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 1        
        label_id = wx.StaticText(panel, label="Set identification command:")
        self.serial_data["idcmd"] = wx.TextCtrl(panel, value="*IDN?")
        get_id = wx.Button(panel, label="Get ID")
        get_id.Bind(wx.EVT_BUTTON, self.GetId)
        grid.Add(label_id, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data["idcmd"], pos=(row, 1), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(get_id, pos=(row, 2), flag=wx.ALL|wx.EXPAND, border=2)
                
        row += 1
        label_id2 = wx.StaticText(panel, label="Id:")
        self.serial_data["id"] = wx.TextCtrl(panel, value="")
        grid.Add(label_id2, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data["id"], pos=(row, 1), span=(0, 2), flag=wx.ALL|wx.EXPAND, border=2)
        row += 1
        
        # add a separator
        row += 1        
        grid.Add(wx.StaticLine(panel), pos=(row, 0), span=(0,3), flag=wx.ALL|wx.EXPAND, border=2)       
        
        row += 1
        label_type = wx.StaticText(panel, label="Type:")
        ins_types = ["Multimeter",
                     "PSU",
                     "Waveform Generator",
                     "Generic"]
        self.serial_data["type"] = wx.ComboBox(panel, choices=ins_types, style=wx.CB_READONLY)
        self.serial_data["type"].SetSelection(0)       
        self.serial_data["type"].Bind(wx.EVT_COMBOBOX, self.OnTypeSelection)
        grid.Add(label_type, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data["type"], pos=(row, 1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 1
        spacer = wx.StaticText(panel)
        grid.Add(spacer, pos=(row, 0), span=(0, 3), flag=wx.ALL|wx.EXPAND, border=2)        
        grid.AddGrowableRow(row)
        
        # add a separator
        row += 1        
        grid.Add(wx.StaticLine(panel), pos=(row, 0), span=(0,3), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 1
        lbl_channel = wx.StaticText(panel, label="Channel:")
        self.spin_channel = wx.SpinCtrl(panel, min=1, max=2, value="1")
        self.spin_channel.Disable()
        grid.Add(lbl_channel, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_channel, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lbl_global = wx.StaticText(panel, label="Global Name:")
        default = defaultname = "ins"
        index = 1
        while defaultname in self._variables:
            defaultname = default + str(index)
            index += 1 
        self.text_global = wx.TextCtrl(panel, value=defaultname)
        grid.Add(lbl_global, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.text_global, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 0)
        sbox_sizer.AddSpacer(10)
        
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        btn_add = wx.Button(panel, label="Add", id=wx.ID_OK)
        btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(btn_add, 0, wx.ALL|wx.EXPAND, 5)
                        
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
    
    def GetId(self, event):
        """ query for instrument ID """
        print(111)
        btn = event.GetEventObject()
        btn.Disable()
        serial = self.serial_data
        baudrate = serial["baudrate"].GetValue()
        port = serial["port"].GetValue()
        bytesize = serial["bytesize"].GetValue()
        stopbits = serial["stopbits"].GetValue()
        flowcontrol = serial["flowcontrol"].GetValue()
        parity = serial["parity"].GetValue()
        timeout = serial["timeout"].GetValue()
        
        ser = sf.OpenSerial(port,baudrate,bytesize,stopbits,parity,flowcontrol,timeout)
        if ser is False:
            btn.Enable()
            print(" could not open serial .retry...")
            return
        cmd = serial["idcmd"].GetValue()
        msg = sf.SendToSerial(ser, cmd)
        print("Received ID:", msg)
        serial["id"].SetValue(msg)
        
        btn.Enable()
        
        
    def OnInstrumentSelection(self, event):        
        e = event.GetEventObject()
        instrument = e.GetValue()    
        instrument = self._instrument_data[instrument]
        
        for option, value in instrument.items():
            if option == "name":
                continue
            self.serial_data[option].SetValue(value)
        
            
        """ enable channel selection if the instrument is a PSU or multimeter """
        if self.serial_data["type"].GetValue() in ["PSU","Multimeter"]:
            self.spin_channel.Enable()
        else:
            self.spin_channel.Disable()
    
    def OnTypeSelection(self, event):
        e = event.GetEventObject()
        instrument = e.GetValue()   
        if instrument in ["PSU","Multimeter"]:
            self.spin_channel.Enable()
        else:
            self.spin_channel.Disable()
            
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
        
        for option in self.serial_options: 
            self.serial_data[option].SetValue(param_dict[option])
        
        if "channel" in param_dict:
            self.spin_channel.SetValue(param_dict["channel"])
            self.spin_channel.Enable()
            
        self.text_global.SetValue(data["global"])
        
    def GetValue(self):
    
        data = []
         
        for option in self.serial_options: 
            data.append((option, self.serial_data[option].GetValue()))
        
        if self.spin_channel.IsEnabled():
            data.append(("channel", str(self.spin_channel.GetValue())))
            
        data = {"action":"Setup Instrument", 
                "parameters":str(data)}
        
        #pass instrument type separately also, so we can append to list
        data["type"] = self.serial_data["type"].GetValue()
        
         
        glob = self.text_global.GetValue()
        if glob != "":
            for char in glob:
                if char.isdigit() or char.isalpha():
                    continue
                glob = glob.replace(char, "_")     
            data["global"] = glob
        else: 
            self.EndModal(wx.ID_CANCEL)
        
           
        return data