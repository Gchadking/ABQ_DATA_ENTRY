import tkinter as tk
from tkinter import ttk
from datetime import datetime
from . import  views as v
from . import models as m

class Application(tk.Tk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title("ABQ Data Entry Application")
        self.resizable(width=True,height=True)
        ttk.Label(self,text="ABQ Data Entry Application",font=("TKDefaultFont",16)).grid(row=0)
        self.recordform=v.DataRecordForm(self,m.CSVModel.fields)
        self.recordform.grid(row=1,padx=10)
        self.savebutton=ttk.Button(self,text="Save",command=self.on_save)
        self.savebutton.grid(row=2,padx=10,sticky=tk.E)
        self.status=tk.StringVar()
        self.statusbar=ttk.Label(self,textvariable=self.status)
        self.statusbar.grid(row=3,padx=10,sticky=tk.W+tk.E)
        self.records_saved=0

    def on_save(self):
        errors=self.recordform.get_errors()
        if errors:
            self.status.set(
                "Cannot save,error in fields: {}".format(', '.join(errors.keys()))
            )
            return False
        datestring=datetime.today().strftime("%Y-%m-%d")
        filename="abq_data_record_{}.csv".format(datestring)
        model=m.CSVModel(filename)
        data=self.recordform.get()
        model.save_record(data)
        self.records_saved += 1

        self.status.set("{} records saved this session".format(self.records_saved))
        self.recordform.reset()
