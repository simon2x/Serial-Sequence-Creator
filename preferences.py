import wx
import base

class PreferencesPage(wx.Panel):

    def __init__(self, parent):
    
        wx.Panel.__init__(self, parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(self)
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        
        self.tree_ids = {}
        self.tree = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT) 
        self.root = self.tree.AddRoot("root")
        # for label in [("General", ),
                      # ("Log", )]:
        sbox_sizer.Add(self.tree, 1, wx.ALL|wx.EXPAND)
         
         
        sizer.Add(sbox_sizer, 1, wx.ALL|wx.EXPAND)
        
        self.SetSizer(sizer)
        
        self.SetMinSize(self.GetSize())
        
    def GetId(self, event):
        """ query for instrument ID """
        btn = event.GetEventObject()
        btn.Disable()
        serial = self.serial_options
        baudrate = serial["baudrate"].GetValue()
        port = serial["port"].GetValue()
        bytesize = serial["bytesize"].GetValue()
        stopbits = serial["stopbits"].GetValue()
        flowcontrol = serial["flowcontrol"].GetValue()
        parity = serial["parity"].GetValue()
        
        ser = ConnectToSerial(port,baudrate,bytesize,stopbits,parity,flowcontrol)
        cmd = self.id_cmd.GetLabel()
        msg = sf.SendToSerial(ser, cmd)
        print(msg)
        self.id.SetLabel(msg)
        if self.name.GetValue() == "":
            self.name.SetValue(msg)
        btn.Enable()