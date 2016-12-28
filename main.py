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
import sys
import time
import wx
import theme
import os
import os.path
from collections import OrderedDict
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
import wx.lib.agw.aui as aui 

#local modules
import instruments
import sequences
import preferences
import serialfunctions as sf


#----- logging -----#

logging.basicConfig(format=format, level=logging.INFO)
logger = logging.getLogger(__name__)

# create file handler which logs even debug messages
fh = logging.FileHandler('ssc.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info('Hello')

#------------------------------------------------#


class Main(wx.Frame):

    def __init__(self):
        
        self._title = "Simple Sequence Creator 0.1"
        
        wx.Frame.__init__(self,
                          parent=None,
                          title=self._title)
                          
        self._defaults = {"preferences": {'pos': '0',
                                          'startup': '0',
                                          'size': '0'},                                    
                          "instruments": {},
                            "sequences": {}}
        
                
        self.getcwd = os.getcwd()
        self._file = "data.json"
        self._file = os.path.join(self.getcwd, "data", self._file)
        self._data = {}         
        
        self._menus = {}
        self._panels = {}
        
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
        
        #-----
        panel = wx.Panel(self)   
        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        
        self.notebook = aui.AuiNotebook(panel, agwStyle=aui.AUI_NB_TAB_MOVE|aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.notebook.SetTabCtrlHeight(32)
        # ----- notebook bindings
        # self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.OnTabClicked)
        # EVT_AUINOTEBOOK_BUTTON
        #-----
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 0)  
        
        panel.SetSizer(sizer)
        panel.Fit()
        # sizer.Fit(self)
        self.SetSize((600, 700))
        self.panel = panel
        
        #-----
        self.CreateMenu()
        self.CreateToolbar()
        self.CreateStatusBar()
        
        #----- create empty file
        self.CreateNewEditor()
        
        #-----
        self.Show()       
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            print("Could not set icon")
            
        
        # configuration
        if self._data["preferences"]["pos"] == "0":
            self.Centre()
        else:   
            x, y = self._data["preferences"]["pos"].split(",")
            self.SetPosition((int(x), int(y)))
            
        if self._data["preferences"]["size"] == "0":
            pass
        else:   
            w, h = self._data["preferences"]["size"].split(",")
            self.SetSize((int(w), int(h)))    
    

    def GetInstrumentData(self):
        """ return an ordered dictionary of instrument data by index """
        instrument_dict = OrderedDict()
        count = len(self._data["instruments"].keys())
        for idx in range(count):
            name = self._data["instruments"][str(idx)]["name"]
            instrument_dict[name] = self._data["instruments"][str(idx)]
            
        return instrument_dict
        
#end GetInstrumentData def

    def OnCloseWindow(self, event):
        # self._data["instruments"] = self._instrument_data
        print (self._data)
        with open(self._file, 'w') as file: 
            json.dump(self._data, file, sort_keys=True, indent=1)
            
        # continue to exit program
        event.Skip()

#end OnCloseWindow def

    def CreateMenu(self):
        menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        file_menus = [("New", "New Sequence"),
                      ("Open...", "Open Sequence"),
                      ("Save", "Save Sequence"),
                      ("Save As...", "Save Sequence As"),
                      ("Exit", "Exit")]
        for item, help_str in file_menus:
            self._menus[item] = menu_file.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenuAndToolBar, self._menus[item])
            
        menu_file.AppendSeparator()
        
        menu_edit = wx.Menu()
        edit_menus = [("Sequence Creator", "Edit Sequences"),
                      ("Create Instrument Presets", "Create Instrument Presets"),
                      ("Preferences", "Edit Preferences")]
        for item, help_str in edit_menus:
            self._menus[item] = menu_edit.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenuAndToolBar, self._menus[item])
      
        menu_help = wx.Menu()
        help_menus = [("About", "About This Program")]
        for item, help_str in help_menus:
            self._menus[item] = menu_help.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenuAndToolBar, self._menus[item])
            
        menubar.Append(menu_file, "&File")
        menubar.Append(menu_edit, "&Edit")
        menubar.Append(menu_help, "&Help")
        
        self.SetMenuBar(menubar)

#end CreateMenu def

    def OnMenuAndToolBar(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        
        try:
            label = e.GetLabel(id).lower()
        except:     
            tool = e.FindById(id) 
            label = tool.GetLabel().lower()
            
        self.DoOperation(label)
 
#end OnMenuAndToolBar def

    def DoOperation(self, label):
        if label == "new": 
            self.CreateNewEditor()            
        elif label == "open...":
            self.OpenFile()            
        elif label == "save": 
            self.SaveFile()            
        elif label == "save as...": 
            self.SaveFileAs()            
        elif label == "import":  
            self.ImportFile()
        elif label == "about":        
            AboutDialog(self)
        elif label in ["instruments","create instrument presets"]:
            dlg = instruments.InstrumentsDialog(self)
            dlg.SetInstrumentData(self._data["instruments"])
            ret = dlg.ShowModal()
            if ret == wx.ID_OK:
                ins_data = dlg.GetValue()
                self._data["instruments"] = ins_data 
                self.SaveData()
            dlg.Destroy()
            
#end DoOperation def
    
    def SaveData(self):
        """ save instruments data and preferences """
        with open(self._file, 'w') as file: 
            json.dump(self._data, file, sort_keys=True, indent=1)
     
#end SaveData def

    def CreateToolbar(self):
        # toolbar = wx.ToolBar(self, style=wx.TB_VERTICAL|wx.TB_TEXT|wx.TB_FLAT)
        toolbar = wx.ToolBar(self)# style=wx.TB_TEXT|wx.TB_FLAT)
        # toolbar.AddTool(wx.ID _ANY, "t")#,  wx.BitmapFromBuffer(wx.ART_FILE_OPEN))
        toolbar.SetToolBitmapSize((16,16))
        
        for label, help, icon in [
            ("New", "Create new sequence file", "psu_png"),
            ("Open", "Open File", "open"), 
            ("Save", "Save File", "save"), 
            ("Save As", "Save File As...", "save"),
            ("Undo", "Undo action", "save"),
            ("Redo", "Redo action", "save"),
            ("Run", "Run Sequence", "save"),
            ("Instruments", "Create Instrument Presets", "save")]:

            if label in ["Instruments"]:    
                toolbar.AddStretchableSpace()
            
            try:
                bmp = theme.GetBitmap(icon)
            except:
                bmp = wx.Bitmap(16,16)
                
            tool = toolbar.AddTool(wx.ID_ANY, label=label, bitmap=bmp, shortHelp=help)
            self.Bind(wx.EVT_TOOL, self.OnMenuAndToolBar, tool)
            
            if label == "Import":
                toolbar.AddSeparator()
            if label == "Save As":
                toolbar.AddSeparator()
            if label == "Fullscreen":
                toolbar.AddSeparator()
            
        toolbar.Realize()
        self.SetToolBar(toolbar)

#end CreateToolbar def
        
    def CreateNewEditor(self):
        """ create a new file without a path specified """        
        title = "untitled"
        ext = ".json"
        new_file = title + ext
        
        notebook = self.notebook
        count = notebook.GetPageCount()
        pages = []
        for index in range(count):
            text = notebook.GetPageText(index)
            pages.append(text)
        
        # is new filename unique?
        index = 1
        while new_file in pages:
            new_file = title + str(index) + ext
            index += 1
        
        new_page = sequences.SequencesPanel(self.notebook, None, new_file)
        
        self.notebook.AddPage(new_page, new_file)
        self.notebook.SetSelection(count)

#end CreateNewEditor def
 
    def OpenFile(self):   
        wildcard = "JSON files (*.json;)|"
        file = wx.FileDialog(self, 
                             defaultDir="",
                             message="Open JSON Sequence file", 
                             wildcard=wildcard,
                             style=wx.FD_DEFAULT_STYLE|wx.FD_FILE_MUST_EXIST)
        
        if file.ShowModal() == wx.ID_CANCEL:
            return
        
        # is file already open? if so, switch to it instead
        for index, page in enumerate(self.notebook.GetChildren()):
            path, py_file = page.GetPathAndFileName()
            if path == file.GetPath():
                self.notebook.SetSelection(index)
                return
        
        path = file.GetPath()
        _, file = os.path.split(path)
        
        #now get data
        new_page = sequences.SequencesPanel(self.notebook, file)
        # new_page.UpdateImageList(data)
        
        page = self.notebook.AddPage(new_page, file)
        self.notebook.SetSelection(page-1)
    
#end OpenFile def

    def SaveFile(self):
        editor = self.notebook.GetPage(self.notebook.GetSelection())
        path, name = editor.GetPathAndFileName()
        
        # no path defined, save file as...
        if path is None:
            wildcard = "JSON files (*.json;)|"
            file = wx.FileDialog(self, 
                                 defaultDir="",
                                 defaultFile=name,
                                 message="Save JSON Sequence File", 
                                 wildcard=wildcard,
                                 style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        
            if file.ShowModal() == wx.ID_CANCEL:
                return
        
            path = file.GetPath()
            _, py_file = os.path.split(path)
            
            # set new filename and path
            editor.SetPathAndFileName(path, py_file)                
        
        # proceed to save file
        editor.SaveFile()  
        
        # py_file won't be defined if no save as
        try:
            # change notebook page text to file name
            self.notebook.SetPageText(self.notebook.GetSelection(), py_file)
        except:
            pass

#end SaveFile def


    def SaveFileAs(self):
        editor = self.notebook.GetChildren()[self.notebook.GetSelection()]
        path, name = editor.GetPathAndFileName()
        
        wildcard = "Python files (*.py;*.pyw;*.ipy)|"
        file = wx.FileDialog(self, 
                             defaultDir=path,
                             defaultFile=name,
                             message="Save PyEmbeddedFile As...", 
                             wildcard=wildcard,
                             style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        
        if file.ShowModal() == wx.ID_CANCEL:
            return
        
        path = file.GetPath()
        _, py_file = os.path.split(path)
        
        # set new filename and path, change notebook tab accordingly
        editor.SetPathAndFileName(path, py_file)            
        
        # proceed to save file
        editor.SaveFile() 
        
        # change notebook page text to file name
        self.notebook.SetPageText(self.notebook.GetSelection(), py_file)
        
#end SaveFileAs def
 
#end Main class

if __name__ == "__main__":
    app = wx.App()    
    Main()
    app.MainLoop()
    