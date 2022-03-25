import tkinter as tk
from tkinter import ttk
from datetime import datetime
from . import  views as v
from . import models as m
from tkinter import messagebox,filedialog
from tkinter.font import nametofont
from .images import ABQ_LOGO

class Application(tk.Tk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.taskbar_icon=tk.PhotoImage(file=ABQ_LOGO)
        self.call('wm','iconphoto',self._w,self.taskbar_icon)#设置应用图标
        self.title("ABQ Data Entry Application")
        self.resizable(width=True,height=True)
        # ttk.Label(self,text="ABQ Data Entry Application",font=("TKDefaultFont",16)).grid(row=0)
        datestring = datetime.today().strftime("%Y-%m-%d")
        default_filename = "abq_data_record_{}.csv".format(datestring)
        self.inserted_rows=[]
        self.updated_rows=[]
        self.filename=tk.StringVar(value=default_filename)
        self.data_model=m.CSVModel(filename=self.filename.get())
        self.setting_model=m.SettingModel()
        self.load_settings()
        style=ttk.Style()
        theme=self.settings.get('theme').get()#设置主题
        if theme in style.theme_names():
            style.theme_use(theme)
        self.settings['theme'].trace('w',self.on_theme_change)
        self.set_font()
        self.settings['font size'].trace('w',self.set_font)#设置字号
        self.callbacks={
            'file->open':self.on_file_select,
            'file->quit':self.quit,
            'show_recordlist':self.show_recordlist,
            'new_record':self.open_record,
            'on_open_record':self.open_record,
            'on_save':self.on_save
        }
        menu=v.MainMenu(self,self.settings,self.callbacks)
        self.config(menu=menu)
        self.recordform=v.DataRecordForm(self,m.CSVModel.fields,self.settings,self.callbacks)
        self.recordform.grid(row=1, padx=10, sticky='NSEW')
        self.recordlist=v.RecordList(self,self.callbacks,inserted=self.inserted_rows,updated=self.updated_rows)
        self.recordlist.grid(row=1,padx=10,sticky='NSEW')
        self.populate_recordlist()

        # self.savebutton=ttk.Button(self,text="Save",command=self.on_save)
        # self.savebutton.grid(row=2,padx=10,sticky=tk.E)
        self.status=tk.StringVar()
        self.statusbar=ttk.Label(self,textvariable=self.status)
        self.statusbar.grid(row=2,padx=10,sticky="we")
        self.records_saved=0


    def on_save(self):
        errors=self.recordform.get_errors()
        message="Cannot save record"
        if errors:
            detail="The following fields have errors: \n *{}".format('\n *'.join(errors.keys()))
            messagebox.showerror(title="Error",message=message,detail=detail)
            return False
        # filename=self.filename.get()
        # model=m.CSVModel(filename)
        data=self.recordform.get()
        rownum=self.recordform.current_record
        try:
           self.data_model.save_record(data,rownum)
        except IndexError as e:
            messagebox.showerror(title='Error',message='Invaid row specified',detail=str(e))
            self.status.set('Tried to update invaild row')
        except Exception as e:
            messagebox.showerror(title='Error', message='Problem saving record', detail=str(e))
            self.status.set('Problem saving record')
        else:
            self.records_saved += 1
            self.status.set("{} records saved this session".format(self.records_saved))
            self.populate_recordlist()

            if rownum is not None:
                self.updated_rows.append(rownum)
            else:
                rownum=len(self.data_model.get_all_records())-1
                self.inserted_rows.append(rownum)
            if self.recordform.current_record is None:
                self.recordform.reset()

    def on_file_select(self):
        filename=filedialog.asksaveasfilename(title='Select the target file for saving records',
                                              defaultextension='.csv',
                                              filetypes=[('Comma-Separated Values','*.csv *.csv')])
        if filename:
            self.filename.set(filename)
            self.data_model=m.CSVModel(filename=self.filename.get())
            self.populate_recordlist()
            self.inserted_rows=[]
            self.updated_rows=[]

    def load_settings(self):
        vartypes={
            'bool':tk.BooleanVar,
            'str':tk.StringVar,
            'int':tk.IntVar,
            'float':tk.DoubleVar
        }
        self.settings={}
        for key ,data in self.setting_model.variables.items():
            vartype=vartypes.get(data['type'],tk.StringVar)
            self.settings[key]=vartype(value=data['value'])
        for var in self.settings.values():
            var.trace('w',self.save_settings)

    def save_settings(self,*args):
        for key ,variable in self.settings.items():
            self.setting_model.set(key,variable.get())
        self.setting_model.save()

    def populate_recordlist(self):
        try:
            rows=self.data_model.get_all_records()
        except Exception as e:
            messagebox.showerror(title='Error')
            detail=str(e)
        else:
            self.recordlist.populate(rows)

    def show_recordlist(self):
        self.recordlist.tkraise() #界面切换，用于显示记录与新增记录

    def open_record(self,rownum=None):
        if rownum is None:
            record=None
        else:
            rownum=int(rownum)
            try:
                record=self.data_model.get_record(rownum)
            except Exception as e:
                messagebox.showerror(title='Error')
                detail=str(e)
                return
        self.recordform.get_record(rownum,record)
        self.recordform.tkraise()

    def set_font(self,*args):
        font_size=self.settings['font size'].get()
        font_names=('TkDefaultFont','TkMenuFont','TkTextFont')
        for font_name in font_names:
            tk_font=nametofont(font_name)
            tk_font.config(size=font_size)

    def on_theme_change(self,*args):
        message="Change requires restart"
        detail=("The changes do not take effect until application restart")
        messagebox.showwarning(title='Warning',message=message,detail=detail)

