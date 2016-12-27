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


class IntegerCompare(wx.Dialog):

    def __init__(self, parent, variables):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Integer Compare")
        
        self.operations = ["+","-","*","/","^","(",")"]
        self._variables = variables
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        lbl_var1 = wx.StaticText(panel, label="variables:")
        grid.Add(lbl_var1, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=2)
        
        choices = variables["locals"]
        for var in variables["globals"]:
            if var in choices:
                continue
            choices.append(var)    
        choices = sorted(choices)
        
        cbox_vars1 = wx.ComboBox(panel, choices=choices, name="var1", style=wx.CB_READONLY) 
        cbox_vars1.Bind(wx.EVT_COMBOBOX, self.OnVarSelected)  
        grid.Add(cbox_vars1, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 1        
        var1_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in self.operations:
            btn = wx.Button(panel, label=label, name="var1", size=(36,22))
            btn.Bind(wx.EVT_BUTTON, self.OnOperationButton)
            var1_hsizer.Add(btn, 0, wx.ALL, 0)         
        grid.Add(var1_hsizer, pos=(row,1), flag=wx.ALL, border=2)
        
        row += 1
        lbl_var1 = wx.StaticText(panel, label="var1 = ")
        self.text_var1 = wx.TextCtrl(panel, value="")
        self.text_var1.Bind(wx.EVT_TEXT, self.OnVarTextChange)
        grid.Add(lbl_var1, pos=(row,0), flag=wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE, border=2)
        grid.Add(self.text_var1, pos=(row,1), span=(0,1), flag=wx.ALL|wx.EXPAND, border=2)
        
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 0)
        
        #-----
        
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer2 = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid2 = wx.GridBagSizer(5,5)
        
        row = 0
        lbl_var2 = wx.StaticText(panel, label="variables:")
        grid2.Add(lbl_var2, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=2)
           
        cbox_vars2 = wx.ComboBox(panel, choices=choices, name="var2", style=wx.CB_READONLY) 
        cbox_vars2.Bind(wx.EVT_COMBOBOX, self.OnVarSelected)  
        grid2.Add(cbox_vars2, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=2)
        
        
        row += 1
        var2_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in self.operations:
            btn = wx.Button(panel, label=label, name="var2", size=(36,22))
            btn.Bind(wx.EVT_BUTTON, self.OnOperationButton)
            var2_hsizer.Add(btn, 0, wx.ALL, 0)
        
        grid2.Add(var2_hsizer, pos=(row,1), flag=wx.ALL, border=2)
        
        row += 1
        lbl_var2 = wx.StaticText(panel, label="var2 = ")
        self.text_var2 = wx.TextCtrl(panel, value="")
        self.text_var2.Bind(wx.EVT_TEXT, self.OnVarTextChange)
        grid2.Add(lbl_var2, pos=(row,0), flag=wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE, border=2)
        grid2.Add(self.text_var2, pos=(row,1), span=(0,1), flag=wx.ALL|wx.EXPAND, border=2)
        
        sbox_sizer2.Add(grid2, 1, wx.ALL|wx.EXPAND, 0)
        
        hsizer.Add(sbox_sizer, 1, wx.ALL|wx.EXPAND, 0)
        hsizer.Add(sbox_sizer2, 1, wx.ALL|wx.EXPAND, 0)
        
        # -----
        sbox = wx.StaticBox(panel, label="Pass/Fail")        
        sbox_sizer3 = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid3 = wx.GridBagSizer(5,5)
        
        row = 0
        lbl_test = wx.StaticText(panel, label="Test:")  
        self.cbox_var_x = wx.ComboBox(panel, choices=["var1","var2"], value="var1", style=wx.CB_READONLY)
        self.cbox_cond = wx.ComboBox(panel, choices=["=",">","<",">=","<="], value="=", style=wx.CB_READONLY)
        self.cbox_var_y = wx.ComboBox(panel, choices=["var1","var2"], value="var2", style=wx.CB_READONLY)
        grid3.Add(lbl_test, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=2)
        grid3.Add(self.cbox_var_x, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=2)
        grid3.Add(self.cbox_cond, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=2)
        grid3.Add(self.cbox_var_y, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 2
        choices = ["continue","terminate"]
        lbl_pass = wx.StaticText(panel, label="On Pass:")          
        self.cbox_onpass = wx.ComboBox(panel, choices=choices, value="continue", style=wx.CB_READONLY)
        grid3.Add(lbl_pass, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=2)
        grid3.Add(self.cbox_onpass, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 1
        lbl_failure = wx.StaticText(panel, label="On Failure:")  
        self.cbox_onfailure = wx.ComboBox(panel, choices=choices, value="continue", style=wx.CB_READONLY)
        grid3.Add(lbl_failure, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=2)
        grid3.Add(self.cbox_onfailure, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=2)
        
        row += 2
        lbl_local = wx.StaticText(panel, label="Local Name:")
        default = defaultname = "test"
        index = 1
        while defaultname in self._variables["locals"]:
            defaultname = default + str(index)
            index += 1        
        self.text_local = wx.TextCtrl(panel, value=defaultname)
        grid3.Add(lbl_local, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid3.Add(self.text_local, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lbl_global = wx.StaticText(panel, label="Global Name:")
        self.text_global = wx.TextCtrl(panel, value="")
        grid3.Add(lbl_global, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        grid3.Add(self.text_global, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        # grid3.AddGrowableCol(0)
        grid3.AddGrowableCol(1)
        grid3.AddGrowableCol(2)
        grid3.AddGrowableCol(3)
        # grid3.AddGrowableCol(4)
        
        sbox_sizer3.Add(grid3, 1, wx.ALL|wx.EXPAND, 0)
        
        #-----
        hsizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        hsizer_controls.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add = wx.Button(panel, label="Add", id=wx.ID_OK)
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        # self.btn_add.Disable()
        hsizer_controls.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer_controls.Add(self.btn_add, 0, wx.ALL|wx.EXPAND, 5)
                        
        #add to main sizer
        # sizer.Add(sbox_sizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sbox_sizer3, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer_controls, 0, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizer(sizer)  
        
        w, h = sizer.Fit(self)
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass
    
    def OnVarTextChange(self, event):
        pass
        
    def OnVarSelected(self, event):
        e = event.GetEventObject()
        name = e.GetName()
        
        if name == "var1":
            tc = self.text_var1            
        elif name == "var2":
            tc = self.text_var2
        
        string = e.GetStringSelection()
        insertion = tc.GetInsertionPoint()
        value = tc.GetValue()
        
        newvalue = value[:insertion] + string + value[insertion:] 
        tc.SetValue(newvalue)
        
        tc.SetInsertionPoint(insertion+len(string))
        
    def OnOperationButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        name = e.GetName()
        if name == "var1": 
            tc = self.text_var1
        elif name == "var2": 
            tc = self.text_var2
            
        insertion = tc.GetInsertionPoint()
        value = tc.GetValue()
        
        newvalue = value[:insertion] + label + value[insertion:] 
        tc.SetValue(newvalue)
        
        tc.SetInsertionPoint(insertion+len(label))
        
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
        
        self.text_var1.SetValue(param_dict["var1"])
        self.text_var2.SetValue(param_dict["var2"])
        self.cbox_onpass.SetValue(param_dict["onpass"])
        self.cbox_onfailure.SetValue(param_dict["onfailure"])
        self.cbox_cond.SetValue(param_dict["cond"])
        
        self.text_local.SetValue(data["local"])
        self.text_global.SetValue(data["global"])
        
    def GetValue(self):
    
        var1 = self.text_var1.GetValue()
        for char in var1:
            if char.isdigit() or char.isalpha():
                continue
            elif char in self.operations:
                continue
            elif char in ["."]:   
                continue
                
            var1 = var1.replace(char, "")  
            
        var2 = self.text_var2.GetValue()
        for char in var2:
            if char.isdigit() or char.isalpha():
                continue
            elif char in self.operations:
                continue
            elif char in ["."]:   
                continue
                
            var2 = var2.replace(char, "")  
        
        data = [("var1", var1),
                ("var2", var2),
                ("onpass", self.cbox_onpass.GetValue()),
                ("onfailure", self.cbox_onfailure.GetValue()),
                ("cond", self.cbox_cond.GetValue())]
                
        data = {"action":"Integer Compare", 
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