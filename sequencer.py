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
import serial
import sys
import time
import wx
import theme
import os
import os.path

from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

#local modules
import instruments
import sequences
import preferences
import serialfunctions as sf

#------------------------------------------------#

class Main(wx.Frame):

    def __init__(self):
    
        wx.Frame.__init__(self,
                          parent=None,
                          title="Simple Sequence Creator 0.1")
                          
        self._defaults = {"preferences": {'pos': '0',
                                          'startup': '0',
                                          'size': '0'},                                    
                          "instruments": {},
                            "sequences": {}}
        
        
        self.getcwd = os.getcwd()
        self._file = "data.json"
        self._file = os.path.join(self.getcwd, "data", self._file)
        self._data = {} 
        #load settings
        try:
            with open(self._file, 'r') as file: 
                self._data = json.load(file)                
        except:             
            # write new config file
            with open(self._file, 'w') as file: 
                json.dump(self._defaults, file, sort_keys=True, indent=1)
                self._data = self._defaults
        file.close()
        #
        self._preferences = self._data["preferences"]
        self._sequences = self._data["sequences"]
        
        self.add_ins_page = None
        self.psu_connection = None
        
        self.SetBackgroundColour("white")
        panel = wx.Panel(self)   
        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        
        # # populate instrument list control
        # self.RefreshInstrumentList()
                
        self.notebook = wx.Notebook(panel)
        self._sequence_page = sequences.SequencesPage(self.notebook)
        self._instrument_page = instruments.InstrumentsPage(self.notebook)
        self._instrument_page.SetInstrumentData(self._data["instruments"])
        self._preferences_page = preferences.PreferencesPage(self.notebook)
        
        self.notebook.AddPage(self._sequence_page, "Sequence Creator")        
        self.notebook.AddPage(self._instrument_page, "Instruments")
        self.notebook.AddPage(self._preferences_page, "Preferences")
        
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 0)  
        
        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.SetMinSize(self.GetSize())
        
        self.panel = panel
        self.CreateStatusBar()
        self.Show()       
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            print("Could not set icon")
            
        #event bindings
        self.timer_update_channel = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.UpdateChannel, self.timer_update_channel)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        # configuration
        if self._preferences["pos"] == "0":
            self.Centre()
        else:   
            x, y = self._preferences["pos"].split(",")
            self.SetPosition((int(x), int(y)))
            
        if self._preferences["size"] == "0":
            pass
        else:   
            w, h = self._preferences["size"].split(",")
            self.SetSize((int(w), int(h)))    
    
    def GetInstrumentData(self):
        return self._instrument_page.GetInstrumentData()
        
    def OnCloseWindow(self, event):
        #load settings
        # try:
        ins_data = self._instrument_page.GetInstrumentData()
        
        self._data["instruments"] = ins_data
        print (self._data)
        with open(self._file, 'w') as file: 
            json.dump(self._data, file, sort_keys=True, indent=1)
        # except:          
            # logging.warning('Failed to save config') 
            # # write new config file
            # pass
                
        # continue to exit program
        event.Skip()
  
    def UpdateChannel(self, event):
        if not self.psu_connection:
            return
        v1 = self.SendToSerial(self.psu_connection, "V1?")
        self.display_voltage1.SetValue(v1)
        
    def DoStepVoltage(self):
        channel = 2 # available channels 0 or 1
        for v in range(0, 15):
            input = "V" + str(channel) + " " + str(v)
            out = self.SendToSerial(self.psu_connection, input)
        
    def ConnectToPSU(self, port): 
        # configure the serial connections (the parameters differs on the device you are connecting to)
        ser = serial.Serial(port=port,
                            baudrate=9600,
                            parity=serial.PARITY_ODD,
                            stopbits=serial.STOPBITS_TWO,
                            bytesize=serial.SEVENBITS)                    
        print(ser)
        ser.isOpen()

        self.psu_connection = ser
        # self.timer_update_channel.Start(1)
        self.DoStepVoltage()
    
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        name = e.GetName()
                        
    def OnMenuConnectPSU(self, event): 
        e = event.GetEventObject()
        id = event.GetId()
        label = e.GetLabel(id)
        model, port = label.split(" - ")
        self.ConnectToPSU(port)
        
    def SendToSerial(self, ser, input):
        end = "\r\n"
        # end = "\n"
        ser.write(bytes(input + end, "utf8"))
        time.sleep(0.2)
        out = ""
        while ser.inWaiting() > 0:
            # print(ser.read(1))
            out += str(ser.read(1), "utf8")
            
        return out
        
    def GetIdentification(self, ser):         
        id = self.SendToSerial(ser, "*IDN?")
        return id
        
#end Main class

if __name__ == "__main__":
    # try:
    app = wx.App()    
    Main()
    app.MainLoop()
    