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

from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

#------------------------------------------------#
# workbench
#------------------------------------------------#

class PowerSupply(wx.Panel):

    def __init__(self, parent, port, data):
        
        wx.Panel.__init__(self, parent)
        
        self.psu_connection = None
        self.port = port
        self.manufacturer = data["manufacturer"]
        self.send_bytes = data["sendbytes"]
        self.end_line = data["endline"]
        self.channels = data["channels"]        
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self)
        text.SetLabel("Note: channel numbers do not necessarily indicate left-to-right" 
                       +" on the power supply itself")
        hsizer.Add(text, 0, wx.ALL|wx.EXPAND, 5)
        
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.volt_channels = {}
        self.amp_channels = {}
        for n in self.channels: 
            channel_box = wx.StaticBox(self, label="Channel " +str(n))
            channel_box_sizer = wx.StaticBoxSizer(channel_box, wx.HORIZONTAL)
            volt_sizer = wx.BoxSizer(wx.VERTICAL)            
            self.volt_channels[n] = wx.TextCtrl(self)
            # self.volt_channels[n].SetFont(DIGITAL_FONT)
            volt_set = wx.Button(self, label="Set V", size=(-1, 24))
            volt_sizer.Add(self.volt_channels[n], 0, wx.ALL|wx.EXPAND, 5)    
            volt_sizer.Add(volt_set, 0, wx.ALL|wx.EXPAND, 5)    
            
            amp_sizer = wx.BoxSizer(wx.VERTICAL)
            self.amp_channels[n] = wx.TextCtrl(self)
            amp_set = wx.Button(self, label="Set A", size=(-1, 24))            
            amp_sizer.Add(self.amp_channels[n], 0, wx.ALL|wx.EXPAND, 5)   
            amp_sizer.Add(amp_set, 0, wx.ALL|wx.EXPAND, 5)   
            
            channel_box_sizer.Add(volt_sizer, 1, wx.ALL|wx.EXPAND, 5)                
            channel_box_sizer.Add(amp_sizer, 1, wx.ALL|wx.EXPAND, 5)
            
            hsizer2.Add(channel_box_sizer, 0, wx.ALL|wx.EXPAND, 5)
             
             
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer2, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.ConnectToPSU(self.port)
    
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
        self.RefreshReadings()
        
    def RefreshReadings(self):
        if not self.psu_connection:
            return
            
        # get voltage of output in Volts
        for ch in self.volt_channels:        
            cmd = "V" +str(ch) + "?" 
            reading = self.SendToSerial(cmd)
            self.volt_channels[ch].SetValue(reading)
    
        # get current limits of output in Amp
        for ch in self.amp_channels:
            cmd = "I" +str(ch) + "?" 
            reading = self.SendToSerial(cmd)
            self.amp_channels[ch].SetValue(reading)
            
    def SendToSerial(self, input):
        end = self.end_line
        ser = self.psu_connection
        ser.write(bytes(input + end, "utf8"))
        time.sleep(0.1)
        out = ""
        while ser.inWaiting() > 0:
            # print(ser.read(1))
            out += str(ser.read(1), "utf8")
            
        return out
        
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
    
class Multimeter(wx.Panel):

    def __init__(self, parent, data):
    
        wx.Panel.__init__(self, parent)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.SetSizer(sizer)
    
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        name = e.GetName()
        
        if name == "Instrument List":
            if label == "Refresh Instruments":
                self.DoRefreshInstruments()
                
