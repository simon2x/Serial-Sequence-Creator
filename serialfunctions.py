
import logging
import serial
import sys
import time
import serial.tools.list_ports


#------------------------------------------------#
# serial connection functions
#------------------------------------------------#

def OpenSerial(port, baudrate, bytesize, stopbits, parity, flowcontrol, timeout): 
    # configure the serial connections (the parameters differs on the device you are connecting to)
 
    if parity == "None":
        parity = serial.PARITY_NONE
    elif parity == "Odd":
        parity = serial.PARITY_ODD
    elif parity == "Even":
        parity = serial.PARITY_EVEN
    elif parity == "MARK":
        parity = serial.PARITY_MARK
    elif parity == "SPACE":
        parity = serial.PARITY_SPACE
        
    ser = serial.Serial()
    ser.baudrate = int(baudrate)
    ser.port = port
    ser.bytesize = int(bytesize)
    ser.parity = parity
    ser.stopbits = int(stopbits)
    ser.timeout = int(timeout)
    
    if flowcontrol.lower() == "xon/xoff":
        ser.xonxoff = 1
    elif flowcontrol.lower() == "rts/cts":
        ser.rtscts = 1
    elif flowcontrol.lower() == "dsr/dtr":
        ser.dsrdtr = 1
    
    if ser.isOpen() is False:
        ser.close()
    
    try:
        ser.open()
    except:
        # logging(" cannot open serial port ")
        return False
    
    return ser 

def SendToSerial(ser, input):
    end = "\r\n"
    # ser.write(bytes(end, "utf8"))
    # ser.write(bytes("*CLS" +end, "utf8"))
    # time.sleep(0.5)
    # ser = self.psu_connection
    
    ser.write(bytes(input + end, "utf8"))
    time.sleep(0.5)
    out = ""
    while ser.inWaiting() > 0:
        # print(ser.read(1))
        try:
            out += str(ser.read(1), "utf8")
        except UnicodeDecodeError:
            print(UnicodeDecodeError) 
    return out      
    