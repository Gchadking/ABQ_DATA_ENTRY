import tkinter as tk
from tkinter import ttk
from datetime import datetime
from . import widgets as w

class DataRecordForm(tk.Frame):
    def __init__(self,parent,fields,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.inputs={}
        min_height_var=tk.DoubleVar(value='-infinity')
        max_height_var=tk.DoubleVar(value='infinity')

        recordinfo=tk.LabelFrame(self,text="Record information")
        self.inputs['Date']=w.LabelInput(recordinfo,"Date",
                                       field_spec=fields['Date'])
        self.inputs['Date'].grid(row=0,column=0)

        self.inputs['Time']=w.LabelInput(recordinfo,"Time",field_spec=fields['Time'])
        self.inputs['Time'].grid(row=0,column=1)
        self.inputs['Technician']=w.LabelInput(recordinfo,"Technician",field_spec=fields['Technician'])
        self.inputs['Technician'].grid(row=0,column=2)
        self.inputs['Lab']=w.LabelInput(recordinfo,"Lab",field_spec=fields['Lab'])
        self.inputs['Lab'].grid(row=1,column=0)
        self.inputs['Plot']=w.LabelInput(recordinfo,"Plot",field_spec=fields['Plot'])
        self.inputs['Plot'].grid(row=1,column=1)
        self.inputs['Seed sample']=w.LabelInput(recordinfo,"Seed sample",field_spec=fields['Seed sample'])
        self.inputs['Seed sample'].grid(row=1,column=2)
        recordinfo.grid(row=0,column=0,sticky=tk.W+tk.E)

        environmentinfo=tk.LabelFrame(self,text="Environment Data")
        self.inputs['Humidity']=w.LabelInput(environmentinfo,"Humidity(g/m3)",field_spec=fields['Humidity'])
        self.inputs['Humidity'].grid(row=0,column=0)
        self.inputs['Light']=w.LabelInput(environmentinfo,"Light(klx)",field_spec=fields['Light'])
        self.inputs['Light'].grid(row=0,column=1)
        self.inputs['Temperature']=w.LabelInput(environmentinfo,"Temperature",field_spec=fields['Temperature'])
        self.inputs['Temperature'].grid(row=0,column=2)

        self.inputs['Equipment Fault']=w.LabelInput(environmentinfo,"Equipment Fault",field_spec=fields['Equipment Fault'])
        self.inputs['Equipment Fault'].grid(row=1,column=0,columnspan=3)

        environmentinfo.grid(row=1,column=0,sticky=tk.W+tk.E)

        plantinfo=tk.LabelFrame(self,text="Plant data")
        self.inputs['Plants']=w.LabelInput(plantinfo,"Plants",field_spec=fields['Plants'])
        self.inputs['Plants'].grid(row=0,column=0)
        self.inputs['Blossoms']=w.LabelInput(plantinfo,"Blossoms",field_spec=fields['Blossoms'])
        self.inputs['Blossoms'].grid(row=0,column=1)
        self.inputs['Fruit']=w.LabelInput(plantinfo,"Fruit",field_spec=fields['Fruit'])
        self.inputs['Fruit'].grid(row=0,column=2)
        self.inputs['Min height']=w.LabelInput(plantinfo,"Min height (cm)",field_spec=fields['Min height'],
                                             input_args={"max_var":max_height_var,"focus_update_var":min_height_var})
        self.inputs['Min height'].grid(row=1,column=0)
        self.inputs['Max height'] = w.LabelInput(plantinfo, "Max height (cm)", field_spec=fields['Max height'],
                                                 input_args={"min_var":min_height_var,
                                                           "focus_update_var":max_height_var})
        self.inputs['Max height'].grid(row=1, column=1)
        self.inputs['Median height'] = w.LabelInput(plantinfo, "Median height (cm)", field_spec=fields['Median height'],
                                               input_args={"min_var":min_height_var,"max_var":max_height_var})
        self.inputs['Median height'].grid(row=1, column=2)
        self.inputs['Notes']=w.LabelInput(self,"Notes",field_spec=fields['Notes'],input_args={"width":75,"height":10})
        self.inputs['Notes'].grid(row=3,column=0,sticky="W")
        plantinfo.grid(row=2,column=0,sticky=tk.W+tk.E)

        self.reset()

    def get(self):
        data={}
        for key,widget in self.inputs.items():
            data[key]=widget.get()
        return data

    def reset(self):
        lab = self.inputs['Lab'].get()
        time = self.inputs['Time'].get()
        technician = self.inputs['Technician'].get()
        plot = self.inputs['Plot'].get()
        plot_values = self.inputs['Plot'].input.cget('values')
        for widget in self.inputs.values():
            widget.set('')

        #Automating
        current_date=datetime.today().strftime('%Y-%m-%d')
        self.inputs['Date'].set(current_date)
        self.inputs['Time'].input.focus()
        if plot not in ('',plot_values[-1]):
            self.inputs['Lab'].set(lab)
            self.inputs['Time'].set(time)
            self.inputs['Technician'].set(technician)
            next_plot_index=plot_values.index(plot)+1
            self.inputs['Plot'].set(plot_values[next_plot_index])
            self.inputs['Seed sample'].input.focus()


    def get_errors(self):
        errors={}
        for key,widget in self.inputs.items():
            if hasattr(widget.input,'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key]=widget.error.get()
        return errors