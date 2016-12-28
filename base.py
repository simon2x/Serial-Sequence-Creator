import wx
import wx.dataview
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

class TreeListCtrl(wx.dataview.TreeListCtrl):
    
    def __init__(self, parent):
        
        style = wx.dataview.TL_CHECKBOX
        wx.dataview.TreeListCtrl.__init__(self, 
                                          parent,
                                          style=style)
    
        
class ToolTip(wx.ToolTip):
    
    def __init__(self, tip):
        
        wx.ToolTip.__init__(self, tip)
        
        self.SetDelay(50)
        self.SetAutoPop(20000)
        
        self.Enable(True)
        # self.SetDelay

class BaseList(wx.ListCtrl, ListCtrlAutoWidthMixin):
    
    def __init__(self, parent, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL):
        
        wx.ListCtrl.__init__(self, parent, style=style)
        ListCtrlAutoWidthMixin.__init__(self)
    
    def DeselectAll(self):
        first = self.GetFirstSelected()
        if first == -1:
            return
            
        self.Select(first, on=0)
        item = first
        while self.GetNextSelected(item) != -1:
            item = self.GetNextSelected(item)
            self.Select(self.GetNextSelected(item), on=0)
        
class ConfirmDialog(wx.Dialog):
    
    def __init__(self, parent, title="", caption=""):
        
        wx.Dialog.__init__(self,
                           parent,
                           style=wx.DEFAULT_DIALOG_STYLE)
        
        self.SetTitle(title)
        
        # panel = wx.Panel(self)        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        caption = wx.StaticText(self, label=caption)
        hsizer.Add(caption, 0, wx.ALL|wx.EXPAND)
        
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        # hsizer2.AddStretchSpacer(0)
        for label, id in [("No", wx.ID_NO), ("Yes", wx.ID_YES)]:
            btn = wx.Button(self, id=id, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizer2.Add(btn, 0, wx.ALL, 2)
            
        sizer.AddSpacer(20)
        sizer.Add(hsizer, 2, wx.ALIGN_CENTRE, 5)
        # sizer.AddStretchSpacer()
        sizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer2, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        
        self.SetSizer(sizer)
        
        #key events binding
        # self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
    
    def OnKeyUp(self, event):
        keycode = event.GetKeyCode()
        
        if keycode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_NO)
        elif keycode == wx.WXK_ENTER:
            self.EndModal(wx.ID_YES)
        event.Skip()
        
    def OnButton(self, event):
        e = event.GetEventObject()
        id = e.GetId()
        self.EndModal(id)

class InputDialog(wx.Dialog):
    
    def __init__(self, parent, title="", caption=""):
        
        wx.Dialog.__init__(self,
                           parent,
                           style=wx.DEFAULT_DIALOG_STYLE)
        
        self.SetTitle(title)
        
        panel = wx.Panel(self)        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # hsizer = wx.BoxSizer(wx.HORIZONTAL)
        caption = wx.StaticText(panel, label=caption)
        # hsizer.Add(caption, 0, wx.ALL|wx.EXPAND)
        
        self.input = wx.TextCtrl(panel, value="")
        
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.AddStretchSpacer()
        for label, id in [("Ok", wx.ID_OK),
                          ("Cancel", wx.ID_CANCEL)]:
            btn = wx.Button(panel, id=id, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizer2.Add(btn, 0, wx.ALL, 2)
            
        sizer.AddSpacer(20)
        sizer.Add(caption, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.input, 0, wx.ALL|wx.EXPAND, 5)
        sizer.AddStretchSpacer()
        sizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer2, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        panel.SetSizer(sizer)
    
        #key events binding
        self.input.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
    
    def OnKeyUp(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif keycode == wx.WXK_RETURN:
            self.EndModal(wx.ID_OK)
        event.Skip()
        
    def GetValue(self):
        return self.input.GetValue()
        
    def OnButton(self, event):
        e = event.GetEventObject()
        id = e.GetId()
        self.EndModal(id)