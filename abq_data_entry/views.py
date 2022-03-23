import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from . import widgets as w

class DataRecordForm(tk.Frame):
    def __init__(self,parent,fields,settings,callbacks,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.settings=settings
        self.callbacks=callbacks
        self.inputs={}
        min_height_var=tk.DoubleVar(value='-infinity')
        max_height_var=tk.DoubleVar(value='infinity')
        self.current_record=None
        self.record_label=ttk.Label()
        self.record_label.grid(row=0,column=0)
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
        recordinfo.grid(row=1,column=0,sticky=tk.W+tk.E)

        environmentinfo=tk.LabelFrame(self,text="Environment Data")
        self.inputs['Humidity']=w.LabelInput(environmentinfo,"Humidity(g/m3)",field_spec=fields['Humidity'])
        self.inputs['Humidity'].grid(row=0,column=0)
        self.inputs['Light']=w.LabelInput(environmentinfo,"Light(klx)",field_spec=fields['Light'])
        self.inputs['Light'].grid(row=0,column=1)
        self.inputs['Temperature']=w.LabelInput(environmentinfo,"Temperature",field_spec=fields['Temperature'])
        self.inputs['Temperature'].grid(row=0,column=2)

        self.inputs['Equipment Fault']=w.LabelInput(environmentinfo,"Equipment Fault",field_spec=fields['Equipment Fault'])
        self.inputs['Equipment Fault'].grid(row=1,column=0,columnspan=3)

        environmentinfo.grid(row=2,column=0,sticky=tk.W+tk.E)

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

        plantinfo.grid(row=3,column=0,sticky=tk.W+tk.E)
        self.inputs['Notes'] = w.LabelInput(self, "Notes", field_spec=fields['Notes'],
                                            input_args={"width": 75, "height": 10})
        self.inputs['Notes'].grid(row=4, column=0, sticky="W")
        self.savebutton=ttk.Button(self,text='Save',command=self.callbacks['on_save'])
        self.savebutton.grid(row=5,padx=10,sticky='e')

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
        if self.settings['autofill date'].get():
            current_date=datetime.today().strftime('%Y-%m-%d')
            self.inputs['Date'].set(current_date)
            self.inputs['Time'].input.focus()
        if (self.settings['autofill sheet data'].get() and  plot not in ('',plot_values[-1])):
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

    def get_record(self,rownum,data=None):
        self.current_record=rownum
        if rownum is None:
            self.reset()
            self.record_label.config(text='New Record')
        else:
            self.record_label.config(text='Record #{}'.format(rownum))
            for key,widget in self.inputs.items():
                self.inputs[key].set(data.get(key,''))
                try:
                    widget.input.trigger_focusout_validation()
                except AttributeError:
                    pass

class MainMenu(tk.Menu):
    def __init__(self,parent,settings,callbacks,**kwargs):
        super().__init__(parent,**kwargs)
        file_menu=tk.Menu(self,tearoff=False)
        file_menu.add_command(
            label="Select file...",
            command=callbacks['file->open']
        )
        file_menu.add_separator()
        file_menu.add_command(label='Quit',command=callbacks['file->quit'])
        self.add_cascade(label='File',menu=file_menu)

        options_menu=tk.Menu(self,tearoff=False)
        options_menu.add_checkbutton(label='Autofill Date',
                                     variable=settings['autofill date'])
        options_menu.add_checkbutton(label='Auto fill sheet data',
                                     variable=settings['autofill sheet data'])
        self.add_cascade(label='Options',menu=options_menu)
        go_menu=tk.Menu(self,tearoff=False)
        go_menu.add_command(label='Record list',command=callbacks['show_recordlist'])
        go_menu.add_command(label='New record',command=callbacks['new_record'])
        self.add_cascade(label='Go',menu=go_menu)

        help_menu=tk.Menu(self,tearoff=False)
        help_menu.add_command(label='About...',command=self.show_about)
        self.add_cascade(label='Help',menu=help_menu)

    def show_about(self):
        about_message='ABQ Data Entry'
        about_detail=('by Zbb\n''for assistance please contact the author.')
        messagebox.showinfo(title='About',message=about_message,detail=about_detail)

class RecordList(tk.Frame):
    column_defs={
        '#0':{'label':'Row','anchor':tk.W},
        'Date':{'label':'Date','width':150,'stretch':True},
        'Time':{'label':'Time'},
        'Lab':{'label':'Lab','width':40},
        'Plot':{'label':'Plot','width':80}
    }
    default_width=100
    default_minwidth=10
    default_anchor=tk.CENTER
    def __init__(self,parent,callbacks,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.callbacks=callbacks
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.treeview=ttk.Treeview(self,
                                   columns=list(self.column_defs.keys())[1:],
                                   selectmode='browse')


        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.config(yscrollcommand=self.scrollbar.set)
        self.treeview.grid(row=0, column=0, sticky='NSEW')
        self.scrollbar.grid(row=0, column=1, sticky='NSW')
        for name,definition in self.column_defs.items():
            label=definition.get('label','')
            anchor=definition.get('anchor',self.default_anchor)
            minwidth=definition.get('minwidth',self.default_minwidth)
            width=definition.get('width',self.default_width)
            stretch=definition.get('stretch',False)
            self.treeview.heading(name,text=label,anchor=anchor)
            self.treeview.column(name,anchor=anchor,minwidth=minwidth,width=width,stretch=stretch)

        self.treeview.bind('<<TreeviewOpen>>',self.on_open_record)

    def populate(self,rows):
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        valuekeys=list(self.column_defs.keys())[1:]
        for rownum,rowdata in enumerate(rows):
            values=[rowdata[key] for key in valuekeys]
            self.treeview.insert('','end',iid=str(rownum),text=str(rownum),values=values)
        if len(rows)>0:
            self.treeview.focus_set()
            self.treeview.selection_set(0)
            self.treeview.focus('0')

    def on_open_record(self,*rags):
        selected_id=self.treeview.selection()[0]
        self.callbacks['on_open_record'](selected_id)

