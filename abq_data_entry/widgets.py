import tkinter as tk
from tkinter import ttk
from datetime import datetime
from decimal import Decimal,InvalidOperation
from .constants import FieldTypes as FT

class ValidatedMixin:
    def __init__(self,*args,error_var=None,**kwargs):
        self.error=error_var or tk.StringVar()
        super().__init__(*args,**kwargs)
        vcmd=self.register(self._validate)
        invcmd=self.register(self._invalid)
        self.config(
            validate='all',
            validatecommand=(vcmd,'%P','%s','%S','%V','%i','%d'),
            invalidcommand=(invcmd,'%P','%s','%S','%V','%i','%d')
            )

    def _toggle_error(self,on=False):
        self.config(foreground=('red' if on else 'black'))

    def _validate(self,proposed,current,char,event,index,action):
        self._toggle_error(False)
        self.error.set('')
        valid=True
        if event =='focusout':
            valid=self._focusout_validate(event=event)
        elif event =='key':
            valid=self._key_validate(proposed=proposed,
                                     current=current,char=char,event=event,
                                     index=index,action=action)
        return valid

    def _focusout_validate(self,**kwargs):
        return True

    def _key_validate(self,**kwargs):
        return True

    def _invalid(self,proposed,current,char,event,index,action):
        if event=='focusout':
            self._focusout_invalid(event=event)
        elif event=='key':
            self._key_invalid(proposed=proposed,
                              current=current,char=char,event=event,
                              index=index,action=action)

    def _focusout_invalid(self,**kwargs):
        self._toggle_error(True)

    def _key_invalid(self,**kwargs):
        pass

    def trigger_focusout_validation(self):
        valid=self._validate('','','','focusout','','')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid


class RequiredEntry(ValidatedMixin,ttk.Entry):
    def _focusout_validate(self,event):
        valid=True
        if not self.get():
            valid=False
            self.error.set("A value is required")
        return valid


class ValidatedCombobox(ValidatedMixin,ttk.Combobox):
    def _key_validate(self,proposed,action,**kwargs):
        valid=True
        if action=='0':
            self.set('')
            return True
        values=self.cget('values')
        matching=[x for x in values if x.lower().startswith(proposed.lower())]
        if len(matching)==0:
            valid=False
        elif len(matching)==1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid=False
        return valid

    def _focusout_validate(self,**kwargs):
        valid=True
        if not self.get():
            valid=False
            self.error.set('A value is required')
        return valid


class ValidatedSpinbox(ValidatedMixin,ttk.Spinbox):
    def __init__(self,*args,min_var=None,max_var=None,
                 focus_update_var=None,from_='-Infinity',
                 to='Infinity',**kwargs):
        super().__init__(*args,from_=from_,to=to,**kwargs)
        self.resolution=Decimal(str(kwargs.get('increment','1.0')))
        self.precision=(self.resolution.normalize().as_tuple().exponent)
        self.variable=kwargs.get('textvariable')or tk.DoubleVar()
        if min_var:
            self.min_var=min_var
            self.min_var.trace('w',self._set_minimum)
        if max_var:
            self.max_var=max_var
            self.max_var.trace('w',self._set_maxmum)
        self.focus_update_var=focus_update_var
        self.bind('<FocusOut>',self._set_focus_update_var)

    def _set_focus_update_var(self,event):
        value=self.get()
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(value)

    def _set_minimum(self,*args):
        current=self.get()
        try:
            new_min=self.min_var.get()
            self.config(from_=new_min)
        except (tk.TclError,ValueError):
            pass
        if not current:
            self.delete(0,tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()

    def _set_maxmum(self,*args):
        current=self.get()
        try:
            new_max=self.max_var.get()
            self.config(to=new_max)
        except (tk.TclError,ValueError):
            pass
        if not current:
            self.delete(0,tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()


    def _key_validate(self,char,index,current,proposed,action,**kwargs):
        valid=True
        min_val=self.cget('from')
        max_val=self.cget('to')
        no_negative=min_val >=0
        no_decimal=self.precision >=0
        if action=='0':
            return True
        if any([
            (char not in ('-1234567890.')),
            (char=='-'and (no_negative or index!='0')),
            (char=='.' and (no_decimal or '.'in current))

        ]):
            return False
        if proposed in '-.':
            return True
        proposed=Decimal(proposed)
        proposed_precision=proposed.as_tuple().exponent
        if any([
            (proposed>max_val),
            (proposed_precision<self.precision)
        ]):
            return False
        return valid

    def _focusout_validate(self,**kwargs):
        valid=True
        value=self.get()
        min_val=self.cget('from')
        try:
            value=Decimal(value)
        except InvalidOperation:
            self.error.set('Invalid number string:{}'.format(value))
            return False
        if value<min_val:
            self.error.set('Value is to low (min{})'.format(value))
            valid=False
        max_val=self.cget('to')
        if value>max_val:
            self.error.set('Value is to high (max{})'.format(value))
            valid=False
        return valid


class DateEntry(ValidatedMixin,ttk.Entry):
    def _key_validate(self,action,index,char,**kwargs):
        valid=True
        if action == '0':
            valid = True
        elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
            valid = char.isdigit()
        elif index in ('4', '7'):
            valid = char == '-'
        else:
            valid = False
        return valid

    def _focusout_validate(self,event):
        valid=True
        if not self.get():
            self.error.set('A value is required')
            valid=False
        try:
            datetime.strptime(self.get(),'%Y-%m-%d')
        except ValueError:
            self.error.set("Invalid date")
            valid=False
        return valid

class LabelInput(tk.Frame):
    field_tpyes={
        FT.string:(RequiredEntry,tk.StringVar),
        FT.string_list:(ValidatedCombobox,tk.StringVar),
        FT.iso_date_string:(DateEntry,tk.StringVar),
        FT.long_string:(tk.Text,lambda :None),
        FT.decimal:(ValidatedSpinbox,tk.DoubleVar),
        FT.integer:(ValidatedSpinbox,tk.IntVar),
        FT.boolean:(ttk.Checkbutton,tk.BooleanVar)
    }
    def __init__(self,parent,label='',input_class=None,
                 input_var=None,input_args=None,label_args=None,
                 field_spec=None,**kwargs):
        super().__init__(parent,**kwargs)
        input_args=input_args or {}
        label_args=label_args or {}
        if field_spec:
            field_type=field_spec.get('type',FT.string)
            input_class=input_class or self.field_tpyes.get(field_type)[0]
            var_type=self.field_tpyes.get(field_type)[1]
            self.variable=input_var if input_var else var_type()
            if 'min' in field_spec and 'from_' not in input_args:
                input_args['from_']=field_spec.get('min')
            if 'max' in field_spec and 'to' not in input_args:
                input_args['to']=field_spec.get('max')
            if 'inc' in field_spec and 'increment' not in input_args:
                input_args['increment']=field_spec.get('inc')
            if 'values' in field_spec and 'values' not in input_args:
                input_args['values']=field_spec.get('values')
        else:
            self.variable=input_var

        if input_class in (ttk.Checkbutton,ttk.Button,ttk.Radiobutton):
            input_args["text"]=label
            input_args["variable"]=self.variable
        else:
            self.label=ttk.Label(self,text=label,**label_args)
            self.label.grid(row=0,column=0,sticky=(tk.W+tk.E))
            input_args["textvariable"]=self.variable

        self.input=input_class(self,**input_args)
        self.input.grid(row=1,column=0,sticky=(tk.W+tk.E))
        self.columnconfigure(0,weight=1)
        self.error=getattr(self.input,'error',tk.StringVar())
        self.error_label=ttk.Label(self,textvariable=self.error)
        self.error_label.grid(row=2,column=0,sticky=(tk.W+tk.E))


    def grid(self,sticky=(tk.W+tk.E),**kwargs):
        super().grid(sticky=sticky,**kwargs)

    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            elif type(self.input)==tk.Text:
                return self.input.get('1.0',tk.END)
            else:
                return self.input.get()
        except (TypeError,tk.TclError):
            return ''

    def set(self,value,*args,**kwargs):
        if type(self.variable)==tk.BooleanVar:
            self.variable.set(bool(value))
        elif self.variable:
            self.variable.set(value,*args,**kwargs)
        elif type(self.input) in (tk.Checkbutton,tk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input)==tk.Text:
            self.input.delete('1.0',tk.END)
            self.input.insert('1.0',value)
        else:
            self.input.delete(0,tk.END)
            self.input.insert(0,value)


