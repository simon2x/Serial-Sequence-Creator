import wx
import logging


#local modules
import base
import serialfunctions as sf
import theme

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class InstrumentsDialog(wx.Dialog):

    def __init__(self, parent):
    
        wx.Dialog.__init__(self, parent, title="Create Instrument Presets")
              
        self.serial_options = ["baudrate",
                               "port",
                               "bytesize",
                               "stopbits",
                               "flowcontrol",
                               "parity",
                               "timeout",
                               "idcmd",
                               "id",
                               "type",
                               "name"]
        self.serial_data = {}
        self._instruments = {}
        self._selected_index = -1
        self.columns = ["#", "Name"]
        
        # main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.splitter = wx.SplitterWindow(self)
        
        # LHS vertical sizer
        left_panel = wx.Panel(self.splitter)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        left_panel.SetSizer(vsizer)
        instrument_list_controls = wx.WrapSizer(wx.HORIZONTAL)
        for label, bmp, binding in [("New", "new", self.OnNewInstrument), ("Remove", "remove", self.OnRemoveInstrument)]:
            try:               
                btn = wx.Button(left_panel, label=label, name="Instrument List", size=(32, 32), style=wx.BU_NOTEXT)
                btn.SetBitmap(theme.GetBitmap(bmp))
            except:
                btn.Destroy()
                btn = wx.Button(left_panel, label=label, name="Instrument List", size=(64, 24))
            btn.Bind(wx.EVT_BUTTON, binding)
            # btn.Bind(wx.EVT_LEFT_DCLICK, self.OnButtonLeftDouble)
            instrument_list_controls.Add(btn, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTRE, 2)
        
        self.instrument_list = base.BaseList(left_panel)        
        for col, name in enumerate(self.columns):
            self.instrument_list.InsertColumn(col, name)                  
        self.instrument_list.setResizeColumn(2)
        self.instrument_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        # self.instrument_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        
        # add to vertical sizer
        vsizer.Add(instrument_list_controls, 0, wx.ALL, 5)
        vsizer.Add(self.instrument_list, 1, wx.ALL|wx.EXPAND, 5)  
        
        # RHS vertical sizer
        right_panel = wx.Panel(self.splitter)
        vsizer2 = wx.BoxSizer(wx.VERTICAL)        
        right_panel.SetSizer(vsizer2)
        
        sbox = wx.StaticBox(right_panel)
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        grid = wx.GridBagSizer(2, 2)
                              
        row = 0
        self._items = [("port", "Port", "COM1"),
                     ("baudrate", "Speed (baud)", "9600", ["110","300","600","1200","2400","4800","9600",
                                                           "14400","19200","28800","38400","56000","57600",
                                                           "115200","128000","153600","230400","256000",
                                                           "460800","921600"]),
                     ("bytesize", "Data bits", "8", [str(x) for x in range(5, 10)]),
                     ("stopbits", "Stop bits", "1", [str(x) for x in range(0, 3)]),
                     ("parity", "Parity", "None", ["None","Odd","Even","Mark","Space"]),
                     ("flowcontrol", "Flow control", "None", ["None","XON/XOFF","RTS/CTS","DSR/DTR"]),
                     ("timeout", "Timeout (s)", "1", [str(x) for x in range(1, 61, 1)])]
        
        
        name, label, default = self._items[0]
        lbl = wx.StaticText(right_panel, label=label)        
        self.serial_data[name] = wx.TextCtrl(right_panel, value=default, name=name)
        grid.Add(lbl, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data[name], pos=(row, 1), flag=wx.ALL|wx.EXPAND, border=2)                
        row += 1
        
        for name, label, default, choices in self._items[1:]:            
            lbl = wx.StaticText(right_panel, label=label)        
            self.serial_data[name] = wx.ComboBox(right_panel, choices=choices, style=wx.CB_READONLY, name=name)
            self.serial_data[name].SetValue(default)
            grid.Add(lbl, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
            grid.Add(self.serial_data[name], pos=(row, 1), flag=wx.ALL|wx.EXPAND, border=2)            
            row += 1
        
            
        # add a separator
        row += 1        
        grid.Add(wx.StaticLine(right_panel), pos=(row, 0), span=(0,3), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 1        
        label_id = wx.StaticText(right_panel, label="Set identification command:")
        self.serial_data["idcmd"] = wx.TextCtrl(right_panel, value="*IDN?", name="idcmd")
        get_id = wx.Button(right_panel, label="Get ID")
        get_id.Bind(wx.EVT_BUTTON, self.GetId)
        grid.Add(label_id, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data["idcmd"], pos=(row, 1), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(get_id, pos=(row, 2), flag=wx.ALL|wx.EXPAND, border=2)
                
        row += 1
        label_id2 = wx.StaticText(right_panel, label="Id:")
        self.serial_data["id"] = wx.TextCtrl(right_panel, value="", name="id")
        grid.Add(label_id2, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data["id"], pos=(row, 1), span=(0, 2), flag=wx.ALL|wx.EXPAND, border=2)
        row += 1
        
        # add a separator
        row += 1        
        grid.Add(wx.StaticLine(right_panel), pos=(row, 0), span=(0,3), flag=wx.ALL|wx.EXPAND, border=2)       
        
        row += 1
        label_type = wx.StaticText(right_panel, label="Type:")
        ins_types = ["Multimeter","PSU","Waveform Generator","Generic"]
        self.serial_data["type"] = wx.ComboBox(right_panel, choices=ins_types, style=wx.CB_READONLY, name="type")
        self.serial_data["type"].SetSelection(0)       
        grid.Add(label_type, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data["type"], pos=(row, 1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 1
        spacer = wx.StaticText(right_panel)
        grid.Add(spacer, pos=(row, 0), span=(0, 3), flag=wx.ALL|wx.EXPAND, border=2)        
        grid.AddGrowableRow(row)
        
        # add a separator
        row += 1        
        grid.Add(wx.StaticLine(right_panel), pos=(row, 0), span=(0,3), flag=wx.ALL|wx.EXPAND, border=2)
        
        
        row += 1
        label_name = wx.StaticText(right_panel, label="Name:")
        self.serial_data["name"] = wx.TextCtrl(right_panel, value="", name="name")
        self.serial_data["name"].Bind(wx.EVT_TEXT, self.OnTextChange)
        grid.Add(label_name, pos=(row, 0), flag=wx.ALL|wx.EXPAND, border=2)
        grid.Add(self.serial_data["name"], pos=(row, 1), span=(0, 2), flag=wx.ALL|wx.EXPAND, border=2)
                
        grid.AddGrowableCol(0)
        grid.AddGrowableCol(1)
        
        sbox_sizer.Add(grid, 4, wx.ALL|wx.EXPAND, 5)
        
        vsizer2.Add(sbox_sizer, 1, wx.ALL|wx.EXPAND, 5)
        
        hsizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, label="Cancel", size=(-1,24))
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        btn_save = wx.Button(self, label="Confirm Changes", size=(-1,24))
        btn_save.Bind(wx.EVT_BUTTON, self.OnConfirm)
        hsizer_controls.Add(btn_cancel, 0, wx.ALL, 5)
        hsizer_controls.Add(btn_save, 0, wx.ALL, 5)
        
        self.splitter.SplitVertically(left_panel, right_panel)
        self.splitter.SetSashGravity(0.3)        
        # add to main sizer        
        sizer.Add(self.splitter, 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add(hsizer_controls, 0, wx.ALL|wx.ALIGN_RIGHT, 2)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.SetMinSize(self.GetBestSize())
        
#end __init__ def
        
    def OnNewInstrument(self, event):
        """ append a new instrument and set its options to the current values """        
        count = self.instrument_list.GetItemCount()
        index = self.instrument_list.Append([str(count), "NewIns"])               
        
        # select and focus
        self.instrument_list.Select(index)
        self.instrument_list.SetFocus()
                
        
#end OnNewInstrument def

    def OnRemoveInstrument(self, event):
        """ query for instrument ID """        
        e = event.GetEventObject()
        label = e.GetLabel()
        
        index = self.instrument_list.GetFirstSelected()
        if index == -1:
            print("no item selected")
            self._instrument_data.SetFocus()
            return
            
        name = self.instrument_list.GetItem(index).GetText()
                        
        dlg = base.ConfirmDialog(self, caption="Delete instrument")
        dlg = dlg.ShowModal()
        if not dlg == wx.ID_YES:
            return
        self.instrument_list.DeleteItem(index)
        del self._instrument_data[name]
        
        self.instrument_list.SetFocus()
        
#end OnRemoveInstrument def

    def OnListItemSelected(self, event):
        """ selecting an item loads its settings """   
        serial = self.serial_data
        
        # before we do anything, save settings of existing
        # selected instrument
        old_index = self._selected_index
        if old_index >= 0:
            try:
                ins_data = self._instruments
                ins_data[str(old_index)] = {}
                
                for option in self.serial_options:
                    try:
                        value = serial[option].GetValue()
                        ins_data[str(old_index)][option] = value
                    except:
                        print("could not get serial option: %s" % option)
                # self._instruments[str(old_index)] = ins_data
            except:
                pass
            print(self._instruments)
            
        # load new 
        index = event.Index        
        self._selected_index = index
        
        try:
            ins_data = self._instruments[str(index)]
        except:
            # if index doesn't exist, use existing values
            ins_data = self._instruments
            ins_data[str(index)] = {}
            
            for option in self.serial_options:
                try:
                    value = serial[option].GetValue()
                    if option == "name":
                        value = "NewIns"
                        serial[option].SetValue(value)
                    ins_data[str(index)][option] = value
                except:
                    print("could not get serial option: %s" % option)
            
            return
            
        # otherwise, load settings
        for option in self.serial_options:
            try:
                print(option)
                serial[option].SetValue(ins_data[option])
            except:
                print("could not set serial option: %s" % option)

                    
#end OnListItemSelected def

    def SetInstrumentData(self, data):
        self._instruments = {}
        # for index, instr in data.items():
            # idx = int(index) 
            # item = self.instrument_list.InsertItem(idx, str(index))
            # self.instrument_list.SetItem(item, 1, instr["name"])
            # self._instruments[index] = instr
            
        count = len(data.keys())    
        for idx in range(count):            
            idx_str = str(idx) 
            instr = data[idx_str]
            
            item = self.instrument_list.InsertItem(idx, idx_str)
            self.instrument_list.SetItem(item, 1, instr["name"])
            self._instruments[idx_str] = instr
            
#end SetInstrumentData def

    def GetValue(self):
        return self._instruments

#end GetValue def

    def OnConfirm(self, event):
        # before closing, save currently selected instrument profile
        selected = self._selected_index
                
        # get serial options
        serial = self.serial_data
        data = {}
        for option in self.serial_options:
            data[option] = serial[option].GetValue()
        self._instruments[str(selected)] = data
        
        self.EndModal(wx.ID_OK)
        
#end OnConfirm def

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        
#end OnCancel def

    def OnTextChange(self, event):
        e = event.GetEventObject()
        index = self.instrument_list.GetFirstSelected()
        
        try:
            name = e.GetValue()
            self.instrument_list.SetItem(index, 1, name)
        except:
            print("cannot change name")
            
#end OnTextChange def

    def GetId(self, event):
        """ query for instrument ID """
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
        if self.name.GetValue() == "":
            self.name.SetValue(msg)
        btn.Enable()
     
#end GetId def

    def OnButtonLeftDouble(self, event):
        pass
        
#end OnButtonLeftDouble def