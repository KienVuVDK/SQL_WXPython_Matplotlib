import wx
import wx.grid as grid
import wx.adv as adv

import matplotlib.figure as figure
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as FigureCanvas , NavigationToolbar2WxAgg as NavigationToolbar)
from matplotlib.animation import FuncAnimation

import pyodbc
import random
import time

from datetime import datetime ,timedelta


now = wx.DateTime.Today()

driver = "ODBC Driver 17 for SQL Server"
server = "DESKTOP-BALESA6\SQLEXPRESS"
database = 'testdb'
username ='sa'
password='sa'
conn = pyodbc.connect('DRIVER={'+driver+'};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
conn1 = pyodbc.connect('DRIVER={'+driver+'};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
conn2 = pyodbc.connect('DRIVER={'+driver+'};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

def ExecuteSQL(cursor,sqlstr):
    cursor.execute(sqlstr)
    return cursor

def ExecuteEdit(cursor,sqlstr):
    cursor.execute(sqlstr)
    conn.commit()
    cursor.close()




class MyFrame(wx.Frame):
    def __init__(self,parent,title):
        super(MyFrame, self).__init__(parent,title=title,size=(1300,750))
        self.parent = MyPanel(self)

class MyPanel(wx.Panel):
    def __init__(self,parent):
        super(MyPanel, self).__init__(parent)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxdata = wx.BoxSizer(wx.VERTICAL)
        self.vboxaxes = wx.BoxSizer(wx.VERTICAL)
        self.hboxdata = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxaxes = wx.BoxSizer(wx.HORIZONTAL)
        self.grid_entry = wx.GridSizer(5,2,5,5)

        self.tst_country = wx.StaticText(self,label='Country')
        self.tst_date = wx.StaticText(self,label="Date")
        self.tst_case = wx.StaticText(self,label="Case")
        self.tst_recovered = wx.StaticText(self,label="Recovered")
        self.tst_dead = wx.StaticText(self,label="Dead")

        self.cbx_country = wx.ComboBox(self)
        self.dpc_date = adv.DatePickerCtrl(self,dt=now)
        self.tct_case = wx.TextCtrl(self)
        self.tct_recovered = wx.TextCtrl(self)
        self.tct_dead = wx.TextCtrl(self)

        self.tgbtn_start = wx.ToggleButton(self,label="Start")
        self.btn_edit = wx.Button(self,label="Edit")
        self.btn_delete = wx.Button(self,label="Delete")

        choice =['Case','Recovered','Dead']
        self.cbx_case = wx.ComboBox(self,choices=choice)
        self.cbx_case.SetValue(self.cbx_case.Items[0])

        self.timer = wx.Timer(self)
        self.top = TopPanel(self)


        self.griddata = grid.Grid(self)

        self.grid_entry.Add(self.tst_country)
        self.grid_entry.Add(self.cbx_country)
        self.grid_entry.Add(self.tst_date)
        self.grid_entry.Add(self.dpc_date)
        self.grid_entry.Add(self.tst_case)
        self.grid_entry.Add(self.tct_case)
        self.grid_entry.Add(self.tst_recovered)
        self.grid_entry.Add(self.tct_recovered)
        self.grid_entry.Add(self.tst_dead)
        self.grid_entry.Add(self.tct_dead)

        self.hboxdata.Add(self.btn_edit)
        self.hboxdata.Add(self.btn_delete)
        self.hboxaxes.Add(self.cbx_case)
        self.hboxaxes.Add(self.tgbtn_start)

        self.vboxdata.Add(self.hboxdata)
        self.vboxdata.Add(self.griddata, 1, wx.EXPAND)

        self.vboxaxes.Add(self.hboxaxes)
        self.vboxaxes.Add(self.top)

        self.hbox.Add(self.vboxdata)
        self.hbox.Add(self.vboxaxes)

        self.vbox.Add(self.grid_entry)
        self.vbox.Add(self.hbox)
        self.Bind(wx.EVT_TIMER,self.lap,self.timer)

        self.SetSizer(self.vbox)

        self.load_combobox()
        self.cbx_country.SetValue(self.cbx_country.Items[0])
        id_country = self.choiceCountry()
        self.load_data(id_country)
        self.ondraw()

        self.cbx_country.Bind(wx.EVT_COMBOBOX,self.onChangeCountry)
        self.cbx_case.Bind(wx.EVT_COMBOBOX, self.onPaint)
        self.tgbtn_start.Bind(wx.EVT_TOGGLEBUTTON,self.onStart)
        self.griddata.Bind(grid.EVT_GRID_CELL_LEFT_CLICK,self.onSelectData)
        self.btn_edit.Bind(wx.EVT_BUTTON,self.onEdit)


    def fill_data(self,id_country):
        self.griddata.SetColLabelValue(0,"Id")
        self.griddata.SetColLabelValue(1,'Date')
        self.griddata.SetColLabelValue(2,'Case')
        self.griddata.SetColLabelValue(3,'Recovered')
        self.griddata.SetColLabelValue(4,'Dead')

        cursor = conn.cursor()
        sql = 'select id_case,date_col,num_case,num_recovered,num_dead from cases where id_country='+str(id_country)
        result_cursor = ExecuteSQL(cursor,sql)
        num_row = 0
        for row in result_cursor:
            id = row[0]
            date = row[1]
            case = row[2]
            recovered = row[3]
            dead = row[4]

            self.griddata.SetCellValue(num_row,0,str(id))
            self.griddata.SetCellValue(num_row, 1, str(date))
            self.griddata.SetCellValue(num_row, 2, str(case))
            self.griddata.SetCellValue(num_row, 3, str(recovered))
            self.griddata.SetCellValue(num_row, 4, str(dead))

            num_row +=1

        cursor.close()

    def load_data(self,id_country):
        cursor = conn.cursor()
        sql = 'select count(*) from cases where id_country='+str(id_country)
        result_cursor = ExecuteSQL(cursor,sql)
        for row in result_cursor:
            self.griddata.CreateGrid(row[0],5)
            self.fill_data(id_country)

    def load_combobox(self):
        cursor = conn.cursor()
        sql = 'select * from country'
        result_cursor =ExecuteSQL(cursor,sql)
        for row in result_cursor:
            self.cbx_country.AppendItems(str(row[0])+'-'+str(row[1]))

    def choiceCountry(self):
        select = self.cbx_country.GetValue()
        array_ctr = select.split('-')
        id_country = array_ctr[0]
        return id_country

    def onChangeCountry(self,event):
        self.fill_data(self.choiceCountry())

    def onSelectData(self,event):
        row = event.GetRow()

        date = self.griddata.GetCellValue(row,1)
        date = date.replace('-','/')
        date = datetime.strptime(date,'%Y/%m/%d')
        case = self.griddata.GetCellValue(row, 2)
        recovered = self.griddata.GetCellValue(row, 3)
        dead = self.griddata.GetCellValue(row, 4)

        self.dpc_date.SetValue(date)
        self.tct_case.SetValue(case)
        self.tct_recovered.SetValue(recovered)
        self.tct_dead.SetValue(dead)
    def onEdit(self,event):
        date = self.dpc_date.GetValue()
        date = str(date).replace(' 12:00:00 SA','')
        date = datetime.strptime(date,'%d/%m/%Y')
        date = datetime.strftime(date, '%d/%m/%Y')
        date = date.split('/')
        day = date[0]
        month = date[1]
        year = date[2]
        date = year+'/'+month+'/'+day

        case = self.tct_case.GetValue()
        recovered = self.tct_recovered.GetValue()
        dead = self.tct_dead.GetValue()
        id_country = self.choiceCountry()

        cursor = conn.cursor()
        sql = 'update cases set num_case = '+str(case)+' , num_recovered = '+str(recovered)+' , num_dead = '+str(dead)+" where date_col = '"+date+"' and id_country = "+id_country
        ExecuteEdit(cursor,sql)
        self.fill_data(id_country)
        self.ondraw()


    def onCollect(self):
        cursor1 = conn1.cursor()
        sql = 'select * from country'
        result_country = ExecuteSQL(cursor1, sql)
        for row_country in result_country:
            id_country = row_country[0]
            country = row_country[1]
            cursor2 = conn2.cursor()
            sql = 'select top 1 id_case,date_col,num_case,num_recovered,num_dead from cases where id_country=' + str(
                id_country) + ' order by id_case desc'
            result_case = ExecuteSQL(cursor2, sql)
            for row_case in result_case:
                date_col = row_case[1]
                num_case = row_case[2]
                num_recovered = row_case[3]
                num_dead = row_case[4]
                date_col = date_col + timedelta(days=1)

                num_case = num_case + random.randrange(int(num_case * 0.1))
                num_recovered = num_recovered + random.randrange(int(num_case * 0.1))
                num_dead = num_dead + random.randrange(int(num_dead * 0.1))

                cursor = conn.cursor()
                sql = 'insert into cases values(' + str(id_country) + ',' + str(num_case) + ',' + str(
                    num_recovered) + ',' + str(num_dead) + ",'" + str(date_col) + "')"
                ExecuteEdit(cursor, sql)
                num_row_old = self.griddata.GetNumberRows()

                cursor = conn.cursor()
                sql = 'select count(*) from cases where id_country=' + str(id_country)
                result_cursor = ExecuteSQL(cursor, sql)
                for row in result_cursor:
                    count = row[0]

                    num_row_add = count - num_row_old
                    self.griddata.AppendRows(num_row_add)
                    self.fill_data(id_country)
                    self.cbx_country.SetValue(str(id_country)+"-"+country)

    def lap(self,event):

        self.onCollect()
        self.ondraw()


    def onStart(self,event):
        state = event.GetEventObject().GetValue()
        if state == True:
            event.GetEventObject().SetLabel("Stop")
            self.timer.Start(2000)

        else:
            event.GetEventObject().SetLabel("Start")
            self.timer.Stop()


    def ondraw(self):
        option = self.cbx_case.GetValue()
        if option =='Case':
            att = 'num_case'
        elif option =='Recovered':
            att = 'num_recovered'
        elif option =='Dead':
            att ='num_dead'
        date = []
        dic = {}
        id_country = []
        country = {}

        cursor = conn.cursor()
        date_country = self.cbx_country.GetValue()
        date_country = date_country.split('-')
        id = date_country[0]

        sql = 'select date_col from cases where id_country = '+id
        result_cursor = ExecuteSQL(cursor, sql)
        for cell in result_cursor:
            date.append(cell[0])
        cursor = conn.cursor()
        sql = 'select * from country'
        result_country = ExecuteSQL(cursor,sql)
        for row in result_country:
            cursor1 = conn1.cursor()
            sql = 'select ' + att + ' from cases where id_country = '+ str(row[0])
            result_cursor = ExecuteSQL(cursor1, sql)
            attribute = []
            for cell in result_cursor:
                attribute.append(cell[0])

            dic[str(row[0])] = attribute
            id_country.append(row[0])
            country[str(row[0])] = row[1]

        self.top.draw(date,option,id_country,country,dic)

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
        #self.axes.style.use('ggplot')

        self.SetSizer(self.sizer)



    def draw(self,date,option,id_country,country,dic):
        self.axes.clear()
        self.axes.set_title("Number of " + option)
        self.axes.set_xlabel("Date")
        self.axes.set_ylabel(option)
        self.axes.grid(True)
        for row in id_country:
            arr = dic[str(row)]
            obje= str(country[str(row)])
            self.axes.plot(date,arr,linestyle='--',linewidth=2,label=obje)
            self.axes.annotate('%0.2f' % arr[len(arr)-1], xy=(1, arr[len(arr)-1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
        self.axes.legend()
        self.canvas.draw()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None,title="Covid")
        self.frame.Show()
        return True

app = MyApp()
app.MainLoop()
