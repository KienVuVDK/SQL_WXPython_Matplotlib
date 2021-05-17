import wx
import wx.grid as grid

import matplotlib.figure as figure
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as FigureCanvas
    ,NavigationToolbar2WxAgg as NavigationToolbar)

import pyodbc

driver = 'ODBC Driver 17 for SQL Server'
server = 'DESKTOP-BALESA6\SQLEXPRESS'
database = 'testdb'
usermane = 'sa'
password = 'sa'
conn = pyodbc.connect('DRIVER={'+driver+'};SERVER='+server+';Database='+database+';UID='+usermane+';PWD='+password)

def ExecuteSQL(cursor,sqlstring):
    cursor.execute(sqlstring)
    return cursor

def ExecuteEdit(cursor,sqlstring):
    cursor.execute(sqlstring)
    conn.commit()
    cursor.close()


class MyFrame(wx.Frame):
    def __init__(self,parent,title):
        super(MyFrame,self).__init__(parent, title=title,size = (1000,1000))

        self.panel = MyPanel(self)

class MyPanel(wx.Panel):
    def __init__(self,parent):
        super(MyPanel,self).__init__(parent)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.gridsz_enter = wx.GridSizer(4,2,10,10)

        self.griddata = grid.Grid(self, pos=(10, 10))
        self.st_age = wx.StaticText(self,label="Age")
        self.st_total = wx.StaticText(self,label="Total")
        self.tct_age = wx.TextCtrl(self)
        self.tct_total = wx.TextCtrl(self)

        self.btn_add = wx.Button(self,label="Add")
        self.btn_edt = wx.Button(self,label="Edit")
        self.btn_delete = wx.Button(self,label="Delete")
        self.btn_paint = wx.Button(self,label = "Paint")

        self.top = TopPanel(self)
        self.ondraw()


        self.gridsz_enter.Add(self.st_age,1)
        self.gridsz_enter.Add(self.tct_age,1)
        self.gridsz_enter.Add(self.st_total,1)
        self.gridsz_enter.Add(self.tct_total,1)

        self.gridsz_enter.Add(self.btn_add)
        self.gridsz_enter.Add(self.btn_edt)
        self.gridsz_enter.Add(self.btn_delete)
        self.gridsz_enter.Add(self.btn_paint)

        self.hbox.Add(self.griddata,1,wx.EXPAND)
        self.hbox.Add(self.top)

        self.vbox.Add(self.gridsz_enter)
        self.vbox.Add(self.hbox)
        self.load_data()

        self.SetSizer(self.vbox)

        self.griddata.Bind(grid.EVT_GRID_SELECT_CELL,self.onChoice)
        self.btn_add.Bind(wx.EVT_BUTTON,self.onAdd)
        self.btn_edt.Bind(wx.EVT_BUTTON,self.onEdit)
        self.btn_delete.Bind(wx.EVT_BUTTON,self.onDelete)
        self.btn_paint.Bind(wx.EVT_BUTTON,self.onPaint)

    # function sql
    def fill_data(self):
        self.griddata.SetColLabelValue(0,"Age")
        self.griddata.SetColLabelValue(1,"Total")
        cursor = conn.cursor()
        sql= "Select * from longevity"

        num_row = 0
        result_cursor = ExecuteSQL(cursor,sql)
        for row in result_cursor:
            r_age = row[0]

            r_total = row[1]
            self.griddata.SetCellValue(num_row,0,str(r_age))
            self.griddata.SetCellValue(num_row,1,str(r_total))
            num_row +=1

        cursor.close()
    def load_data(self):
        cursor = conn.cursor()
        sql = "select * from longevity"
        result_cursor = ExecuteSQL(cursor,sql)
        count = 0
        for row in result_cursor:
            count +=1
        self.griddata.CreateGrid(count,2)
        self.fill_data()

    def onAdd(self,event):
        age =  self.tct_age.GetValue()
        total = self.tct_total.GetValue()
        if age!='' and total !='':
            cursor = conn.cursor()
            sql = 'insert into longevity values ('+age+','+total+')'
            ExecuteEdit(cursor,sql)
            num_row_old = self.griddata.GetNumberRows()

            cursor = conn.cursor()
            sql = 'Select count(*) from longevity'
            result_cursor = ExecuteSQL(cursor,sql)
            for row in result_cursor:
                count = row[0]
            add_row = count-num_row_old
            self.griddata.AppendRows(add_row)
            self.fill_data()
    def onChoice(self,event):
        row = event.GetRow()

        age = self.griddata.GetCellValue(row,0)
        total = self.griddata.GetCellValue(row,1)
        self.tct_age.SetValue(age)
        self.tct_total.SetValue(total)
    def onEdit(self,event):
        age = self.tct_age.GetValue()
        total = self.tct_total.GetValue()

        if age !='' and total != '':
            cursor = conn.cursor()
            sql = 'update longevity set total = '+total+' where age ='+age
            ExecuteEdit(cursor,sql)
            self.fill_data()
    def onDelete(self,event):
        age = self.tct_age.GetValue()
        if age!='':
            cursor = conn.cursor()
            sql = 'delete from longevity where age = '+age
            ExecuteEdit(cursor,sql)

            self.griddata.DeleteRows(self.griddata.GetNumberRows()-1)
            self.fill_data()
    def ondraw(self):
        age = []
        total = []
        cursor = conn.cursor()
        sql = 'select * from longevity'
        result_cursor = ExecuteSQL(cursor, sql)
        for cell in result_cursor:
            age.append(cell[0])
            total.append(cell[1])
        self.top.draw(age, total)
    def onPaint(self,event):
        self.ondraw()

class TopPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.figure = figure.Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.axes.style.use('ggplot')

        self.SetSizer(self.sizer)


    def draw(self,x,y):
        self.axes.clear()
        self.axes.set_title("Khao sat dan so theo tuoi")
        self.axes.set_xlabel("Ages")
        self.axes.set_ylabel("Total")
        self.axes.grid(True)
        self.axes.plot(x,y,color="#f73628",linestyle='--',linewidth=3,marker='x',label='Viet Nam')
        self.axes.legend()
        self.canvas.draw()



class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None,title="Khao sat do tuoi")
        self.frame.Show()
        return True

app = MyApp()
app.MainLoop()