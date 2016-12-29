import wx
import base
import dialogs 
from collections import OrderedDict
import wx.dataview #for TreeListCtrl
from instructions import *
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

class SequencesPanel(wx.Panel):

    def __init__(self, parent, path, name):
        
        wx.Panel.__init__(self, parent)
        
        #-----
        self._name = name
        self._path = path
        
        #-----
        self._undo_stack = []
        self._redo_stack = []
        
        #-----
        self._sequences = []
        self._sequence_data = {}
        self._variables = {"locals":{"Main":[]}, "globals": []}
        self._instruments = {"PSU":[],"Multimeter":[],"Generic":[],"Waveform Generator":[]}
        self._functions = []
        
        #-----
        sbox = wx.StaticBox(self)
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        
        cmd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cmd_vsizer = wx.BoxSizer(wx.VERTICAL)
        cmd_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_filter = wx.StaticText(self, label="Filter:")
        choices = ["None", 
                   "DMM (Digital Multimeter)", 
                   "INS (General)",
                   "PSU (Power Supply)"]
        cbox_filter = wx.ComboBox(self, choices=choices, value=choices[0], style=wx.CB_READONLY)
        cbox_filter.Bind(wx.EVT_COMBOBOX, self.OnFilter)
        cmd_hsizer.Add(lbl_filter, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        cmd_hsizer.Add(cbox_filter, 0, wx.ALL|wx.EXPAND, 2)
        cmd_vsizer.Add(cmd_hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
        self.commands_list = base.BaseList(self)
        self.commands_list.InsertColumn(0, "Instrument")
        self.commands_list.InsertColumn(1, "Instruction Type")
        self.commands_list.InsertColumn(2, "Action")        
        self.commands_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivated)
        for cmd in INSTRUCTIONS:
            item = self.commands_list.Append(cmd)            
        cmd_vsizer.Add(self.commands_list, 1, wx.ALL|wx.EXPAND, 2)                
        
        cmd_hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["+Delay","+Action"]:
            btn = wx.Button(self, label=label, size=(-1, 22))
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            cmd_hsizer2.Add(btn, 0, wx.ALL|wx.EXPAND, 0)
        cmd_vsizer.Add(cmd_hsizer2, 0, wx.ALL|wx.ALIGN_RIGHT, 2)
        
        test_vsizer = wx.BoxSizer(wx.VERTICAL)
        
        test_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_filter = wx.StaticText(self, label="Filter:")
        choices = ["None", 
                   "DMM (Digital Multimeter)", 
                   "INS (General)",
                   "PSU (Power Supply)"]
        cbox_filter = wx.ComboBox(self, choices=choices, value=choices[0], style=wx.CB_READONLY)
        cbox_filter.Bind(wx.EVT_COMBOBOX, self.OnFilter)
        test_hsizer.Add(lbl_filter, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        test_hsizer.Add(cbox_filter, 0, wx.ALL|wx.EXPAND, 2)
        test_vsizer.Add(test_hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
        self.test_list = base.BaseList(self)
        self.test_list.InsertColumn(0, "Pass/Fail Tests")     
        self.test_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnTestButton)
        for cmd in TESTS:
            item = self.test_list.Append([cmd])            
        test_vsizer.Add(self.test_list, 1, wx.ALL|wx.EXPAND, 2)   
        
        test_hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["+Test"]:
            btn = wx.Button(self, label=label, size=(-1, 22))
            btn.Bind(wx.EVT_BUTTON, self.OnTestButton)
            test_hsizer2.Add(btn, 0, wx.ALL|wx.EXPAND, 0)
        test_vsizer.Add(test_hsizer2, 0, wx.ALL|wx.ALIGN_RIGHT, 2)
        
        cmd_sizer.Add(cmd_vsizer, 2, wx.ALL|wx.EXPAND, 5)
        cmd_sizer.Add(test_vsizer, 1, wx.ALL|wx.EXPAND, 5)
        
        sbox_sizer.Add(cmd_sizer, 1, wx.ALL|wx.EXPAND, 5)
        sbox_sizer.AddSpacer(8)
        sbox_sizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 0)
        sbox_sizer.AddSpacer(2)
        
        # the bottom half
        sequence_vsizer = wx.BoxSizer(wx.VERTICAL)
        sequence_controls_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["+Func","Up","Down","Edit","Toggle","Delete"]:
            btn = wx.Button(self, label=label, size=(48, 22))
            if label == "Edit":
                btn.Bind(wx.EVT_BUTTON, self.OnEdit)
            else:
                btn.Bind(wx.EVT_BUTTON, self.OnButton)
            if label in ["Delete"]:
                sequence_controls_hsizer.AddStretchSpacer()
            sequence_controls_hsizer.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        sequence_vsizer.Add(sequence_controls_hsizer, 0, wx.ALL|wx.EXPAND, 0)
              
        self.sequence_items = {}
        self.sequence_tree = base.TreeListCtrl(self)
        for header in ["Action","Local","Global"]:
            self.sequence_tree.AppendColumn(header)
        self.sequence_tree.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.UpdateStatusBar)
        self.sequence_items["0"] = self.sequence_tree.GetRootItem()
        self.sequence_items["0,0"] = self.sequence_tree.AppendItem(self.sequence_items["0"], "Setup")
        
        self.sequence_items["0,1"] = self.sequence_tree.AppendItem(self.sequence_items["0"], "Main")
        
        for index, data in self.sequence_items.items():
            data = index.split(",")
            self.sequence_tree.SetItemData(self.sequence_items[index], data) 
            
        self.sequence_tree.CheckItem(self.sequence_items["0,0"])
        self.sequence_tree.CheckItem(self.sequence_items["0,1"])
        self.sequence_tree.SetColumnWidth(1, wx.COL_WIDTH_AUTOSIZE)
        # self.tree_ids[0] = self.sequence_tree.AddRoot("root")        
        sequence_vsizer.Add(self.sequence_tree, 1, wx.ALL|wx.EXPAND, 5)
        
        sbox_sizer.Add(sequence_vsizer, 1, wx.ALL|wx.EXPAND, 2)       
        
        # sbox_sizer.AddSpacer(5)
                
        self.SetSizer(sbox_sizer)
        
        #----- bindings -----#
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        
#end __init__ def    

    def OnFilter(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        self.commands_list.DeleteAllItems()
        
        filter = None
        if value == "DMM (Digital Multimeter)":
            filter = "DMM"
        elif value == "INS (General)":
            filter = "INS"
        elif value == "PSU (Power Supply)":
            filter = "PSU"
        
        for cmd in INSTRUCTIONS:
            if filter is None:
                item = self.commands_list.Append(cmd)
            elif cmd[0] == filter:
                item = self.commands_list.Append(cmd)
    
#end OnFilter def
   
    def OnTestButton(self, event):
        selection = self.test_list.GetFocusedItem()
        if selection == -1:
            print("no test selected")
            return
        toplevel = self.GetTopLevel()
        if not toplevel:
            print("no tree sequence item selected")
            return
        if toplevel == "Setup":
            print(" cannot be in setup ")
            return
            
        text = self.test_list.GetItemText(selection).lower()
        variables = {"locals":self._variables["locals"][toplevel],
                     "globals":self._variables["globals"]}
        if text == "integer compare":
            dlg = dialogs.integercompare.IntegerCompare(self, variables)
        elif text == "float compare":
            dlg = dialogs.floatcompare.FloatCompare(self, variables)
        elif text == "string compare":
            dlg = dialogs.stringcompare.StringCompare(self, variables)
        elif text == "voltage compare":
            dlg = dialogs.voltagecompare.VoltageCompare(self, variables)
        elif text == "set voltage":
            instruments = sorted(self._instruments["PSU"])
            dlg = dialogs.setvoltage.SetVoltage(self, instruments)
        
        ret = dlg.ShowModal()
        if ret != wx.ID_OK: 
            return
            
        data = dlg.GetValue()
        selection = self.sequence_tree.GetSelection()            
        newitem = self.sequence_tree.AppendItem(selection, data["action"] + " >> " + str(data["parameters"]))
        scope = toplevel
        if "local" in data:
            self.sequence_tree.SetItemText(newitem, 1, data["local"])
            self._variables["locals"][scope].append(data["local"])
        if "global" in data:
            self.sequence_tree.SetItemText(newitem, 2, data["global"])
            self._variables["globals"].append(data["global"])
        
        # postitem = self.sequence_tree.AppendItem(newitem, "Post Action")
        # self.sequence_tree.SetItemText(newitem, 2, str(data["parameters"]))
        self.sequence_tree.Select(newitem)
        self.sequence_tree.CheckItem(newitem)
        self.sequence_tree.Expand(self.sequence_tree.GetSelection())
        self.sequence_tree.SetFocus()

        #----- get new index -----#
        selection_index = self.sequence_tree.GetItemData(selection)
        index = 0
        new_index = [n for n in selection_index]
        new_index_str = ",".join(selection_index) + ","
        while new_index_str + str(index) in self.sequence_items:
            index += 1
        new_index_str += str(index)
        new_index.append(str( index ))
        print(new_index_str,new_index)
        self.sequence_items[new_index_str] = newitem
        self.sequence_tree.SetItemData(newitem, new_index)
        
#end OnTestButton def

    def OnEdit(self, event):
        selection = self.sequence_tree.GetSelection()
        if selection == -1:
            print("no item selected")
            return
        toplevel = self.GetTopLevel()
        if not toplevel:
            print("no tree sequence item selected")
            return
        
        text = self.sequence_tree.GetItemText(selection)
        if text in ["Setup","Main"]:
            print("cannot edit setup or main")
            return
        
        #temporarily remove selected local and global name
        variables = {}
        if toplevel != "Setup":
            locals = [var for var in self._variables["locals"][toplevel]]
            local = self.sequence_tree.GetItemText(selection, 1)
            if local != "":            
                local_idx = locals.index(local)
                del locals[local_idx]
            variables["locals"] = locals
            
        globs = [var for var in self._variables["globals"]]
        glob = self.sequence_tree.GetItemText(selection, 2)
        if glob != "":
            glob_idx = globs.index(glob)
            del globs[glob_idx]
            
        variables["globals"] = globs
       
                     
        if text in self._functions:
            #edit functions            
            dlg = dialogs.addfunction.AddFunction(self)
            dlg.SetValue(text)
            ret = dlg.ShowModal()
            if ret != wx.ID_OK: 
                return
            data = dlg.GetValue()  
            newname = data
            self.sequence_tree.SetItemText(selection, 0, newname)
            
            if text != newname:
                idx = self._functions.index(text)
                del self._functions[idx]
                self._functions.append(newname)
                
                #move variables to new scope
                self._variables["locals"][newname] = self._variables["locals"][text] 
                #and delete old scope
                del self._variables["locals"][text]
                self.sequence_tree.SetFocus()
            return
            
        print(text.split(" >> "))
        action, params = text.split(" >> ")
        try:
            data = {"parameters":params,"local":local,"global":glob}
        except:
            data = {"parameters":params,"global":glob}
            
        action = action.lower()
        dlg = None
        if action == "integer compare":
            dlg = dialogs.integercompare.IntegerCompare(self, variables)
        elif action == "float compare":
            dlg = dialogs.floatcompare.FloatCompare(self, variables)
        elif action == "string compare":
            dlg = dialogs.stringcompare.StringCompare(self, variables)
        elif action == "voltage compare":
            dlg = dialogs.voltagecompare.VoltageCompare(self, variables)        
        elif action == "delay": 
            dlg = dialogs.delay.AddDelay(self)        
        else:
            data = self.OpenDialog(action, variables, data)            
            if not data:
                return
        # if a test
        if dlg: 
            # set the values first
            dlg.SetValue(data)
            ret = dlg.ShowModal()
            if ret != wx.ID_OK: 
                return
            
            data = dlg.GetValue()
            
        self.sequence_tree.SetItemText(selection, 0, data["action"] + " >> " + data["parameters"])    
        
        scope = toplevel
        if "local" in data:
            self.sequence_tree.SetItemText(selection, 1, data["local"])
            locals.append(data["local"])
            self._variables["locals"][scope] = locals
        if "global" in data:
            globs.append(data["global"])
            self.sequence_tree.SetItemText(selection, 2, data["global"])
            self._variables["globals"] = globs
         
        # print(self._variables["globals"], data["global"])  
        
        self.sequence_tree.SetFocus()
                
#end OnEdit def

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        if label == "New":
            dlg = base.InputDialog(self, "New sequence", "Enter new sequence name:")
            ret = dlg.ShowModal()
            if ret == wx.ID_OK:
                name = dlg.GetValue()
                if name != "" and name not in self._sequences:
                    self._sequences.append(name)
                    # self._sequences = sorted(self._sequences)
                    item = self.sequence_list.Append([name])
                    self.sequence_list.DeselectAll()
                    self.sequence_list.Select(item)
                    self.sequence_list.SetFocus()
            dlg.Destroy()
            
        elif label == "+Func":
            dlg = dialogs.addfunction.AddFunction(self)
            ret = dlg.ShowModal()
            if ret == wx.ID_OK:
                name = dlg.GetValue()
                if name in self._functions:
                    return
                self._functions.append(name)
                self._variables["locals"][name] = [] #add local scope
                item = self.sequence_tree.AppendItem(self.sequence_tree.GetRootItem(), name)
                self.sequence_tree.Select(item)
                self.sequence_tree.CheckItem(item)
                self.sequence_tree.SetFocus()
            dlg.Destroy()
            
        elif label == "Remove":        
            dlg = base.ConfirmDialog(self, "Remove selected sequences")
            
        elif label == "+Delay":
            
            selection = self.sequence_tree.GetSelection()
            if self.GetTopLevel() == "Setup":
                return
            data = self.OpenDialog(label)
            item = self.sequence_tree.AppendItem(selection, data["action"] + " >> " + data["parameters"])
            self.sequence_tree.Select(item)
            self.sequence_tree.CheckItem(item)
            self.sequence_tree.SetFocus()
            
        elif label == "+Action":
            row = self.commands_list.GetFocusedItem()
            if row == -1:
                return
                
            count = self.commands_list.GetColumnCount()
            columns = {self.commands_list.GetColumn(i).GetText():i for i in range(0,count)}
            text = self.commands_list.GetItem(row, columns["Action"]).GetText()
            
            # check if we can add this to the selected tree item
            data = self.OpenDialog(text)
            print(" data ", data )
            
            if text == "setup instrument":
                selection = self.sequence_items["setup"]
                self._instruments[data["parameters"]["type"]].append(data["global"])
            else:    
                selection = self.sequence_tree.GetSelection()
                if not selection.IsOk():
                    selection = self.sequence_items["main"]
                
            newitem = self.sequence_tree.AppendItem(selection, data["action"] + " >> " + str(data["parameters"]))
            
            scope = self.GetTopLevel()
            if "local" in data:
                self.sequence_tree.SetItemText(newitem, 1, data["local"])
                self._variables["locals"][scope].append(data["local"])
            if "global" in data:
                self.sequence_tree.SetItemText(newitem, 2, data["global"])
                self._variables["globals"].append(data["global"])
                
            # postitem = self.sequence_tree.AppendItem(newitem, "Post Action")        
            # self.sequence_tree.SetItemText(newitem, 2, str(data["parameters"]))
            self.sequence_tree.Select(newitem)
            self.sequence_tree.CheckItem(newitem)
            self.sequence_tree.Expand(self.sequence_tree.GetSelection())
            self.sequence_tree.SetFocus()
    
#end OnButton def
    
    def GetTopLevel(self):
        """ return sequence tree top-level """
        try:
            selection = item = self.sequence_tree.GetSelection()
        except:
            return False
        
        if not selection.IsOk():    
            return False
            
        text = self.sequence_tree.GetItemText(selection)
      
        # root = self.sequence_tree.GetRootItem()
        # parent = self.sequence_tree.GetItemParent(selection)
        
        parents = [item]
        # get item parents
        while self.sequence_tree.GetItemParent(item).IsOk():            
            parent = self.sequence_tree.GetItemParent(item)     
            parents.append(parent)
            item = parent
            
        parents = [self.sequence_tree.GetItemText(itm) for itm in parents if itm.IsOk()]
        print( parents )
        return parents[-2]
        
#end GetTopLevel def
        
    def OpenDialog(self, label, variables=None, data=None):               
        label = label.lower()
        
        selection = None 
        scope = None
       
        if label == "setup instrument":
            instrument_data = self.GetTopLevelParent().GetInstrumentData()
            # instrument names
            if not variables:
                variables = self._variables["globals"]
            else:
                variables = variables   
        else:
            scope = self.GetTopLevel()
            if not variables:
                variables = {"locals":self._variables["locals"][scope], 
                             "globals":self._variables["globals"]}
            else:
                variables = variables

        if label == "+delay":
            dlg = dialogs.delay.AddDelay(self)
        elif label == "call function":
            functions = self._functions
            # toplevel = self.GetTopLevel()
            # del functions[functions.index(toplevel)]
            dlg = dialogs.callfunction.CallFunction(self, functions, variables)
        elif label == "set voltage":
            instruments = self.GetTopLevelParent().GetInstrumentNames("PSU")
            dlg = dialogs.setvoltage.SetVoltage(self, instruments)
        elif label == "step voltage":
            instruments = sorted(self._instruments["PSU"])
            dlg = dialogs.stepvoltage.StepVoltage(self, instruments, variables)
        elif label == "power off instrument":
            dialogs.AddStepVoltage(self)
        elif label == "send and receive message":
            instruments = []
            for type in self._instruments.keys():
                instruments.extend(self._instruments[type])
                instruments = sorted(instruments)
            dlg = dialogs.sendreceive.SendReceive(self, instruments, variables)
        elif label == "set current limit":
            dlg = dialogs.SendRecieve(self)
        elif label == "read voltage":
            dlg = dialogs.readvoltage.ReadVoltage(self, variables)    
        elif label == "setup instrument":
            dlg = dialogs.setup.SetupInstruments(self, instrument_data, variables)   
        
        if data:
            dlg.SetValue(data)
        ret = dlg.ShowModal()
        if ret != wx.ID_OK: 
            return None
        
        data = dlg.GetValue()
        return data

#end OpenDialog def
                
    def OnListItemActivated(self, event):
        row = event.Index
        count = self.commands_list.GetColumnCount()
        columns = {self.commands_list.GetColumn(i).GetText():i for i in range(0,count)}
        text = self.commands_list.GetItem(row, columns["Action"]).GetText()

        text = text.lower()    
        data = self.OpenDialog(text)
        
        if not data:
            return
        if text == "setup instrument":
            selection = self.sequence_items["0,0"]
            self._instruments[data["type"]].append(data["global"])
        else:    
            selection = self.sequence_tree.GetSelection()
            if not selection.IsOk():
                selection = self.sequence_items["0,1"]
            
        newitem = self.sequence_tree.AppendItem(selection, data["action"] + " >> " + str(data["parameters"]))
                
        if "local" in data:
            scope = self.GetTopLevel()
            self.sequence_tree.SetItemText(newitem, 1, data["local"])
            self._variables["locals"][scope].append(data["local"])
        if "global" in data:
            self.sequence_tree.SetItemText(newitem, 2, data["global"])
            self._variables["globals"].append(data["global"])
            
        # postitem = self.sequence_tree.AppendItem(newitem, "Post Action")        
        # self.sequence_tree.SetItemText(newitem, 2, str(data["parameters"]))
        self.sequence_tree.Select(newitem)
        self.sequence_tree.CheckItem(newitem)
        self.sequence_tree.Expand(self.sequence_tree.GetSelection())
        self.sequence_tree.SetFocus()
                
    def OnFocus(self, event):
        """ on change of page, set the title to the file path"""    
        editor = self.notebook.GetPage(self.notebook.GetSelection())
        path, name = editor.GetPathAndFileName()
        
        if path is None: 
            self.SetTitle(name + " - " + self._title)
        else:
            self.SetTitle(path + " - " + self._title)
        
        event.Skip()
        
#end OnListItemActivated def

    def UpdateStatusBar(self, event=None):
        """ update status bar when selecting a tree item on sequence"""
        selection = self.sequence_tree.GetSelection()
        status = self.sequence_tree.GetItemText(selection)
        print( status )
        self.GetTopLevelParent().SetStatusText(status)
       
        if event:
            event.Skip()

#end UpdateStatusBar def

    def GetPathAndFileName(self):
        """ needed when a file is saved """
        return (self._path, self._name) 

#end GetPathAndFileName def

    def SetPathAndFileName(self, path, name):
        """ needed when a file is saved """
        self._path = path
        self._name = name

#end SetPathAndFileName def

    def SaveFile(self, file=None):
        """ needed when a file is saved """
        print(self.sequence_items)
        def get_item_depth(item):
            """ it's rate great backwards """
            depth = 0
            while tree.GetItemParent(item).IsOk():
                depth += 1 
                item = tree.GetItemParent(item)
            return depth - 1
            
        def get_item_data_list(item):
            parent = get_item_level(item)
            parent = tree.GetItemText()
            itemdata = [tree.GetItemText(item, col) for col in range(count)]
            return itemdata
        
#end SaveFile def