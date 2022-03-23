import csv
import os
from .constants import FieldTypes as FT
import json
class CSVModel:
    """ CSV file storage"""
    fields={
        "Date":{'req':True,'type':FT.iso_date_string},
        "Time":{'req':True,'type':FT.string_list,
                'values':['8:00','12:00','16:00','20:00']},
        "Technician":{'req':True,'type':FT.string},
        "Lab":{'req':True,'type':FT.string_list,
               'values':['A','B','C','D','E']},
        "Plot":{'req':True,'type':FT.string_list,
                'values':[str(x) for x in range(1,21)]},
        "Seed sample":{'req':True,'type':FT.string},
        "Humidity":{'req':True,'type':FT.decimal,
                    'min':0.5,'max':52.0,'inc':.01},
        "Light":{'req':True,'type':FT.decimal,
                 'min':0,'max':100.0,'inc':.01},
        "Temperature":{'req':True,'type':FT.decimal,
                       'min':4,'max':40,'inc':.01},
        "Equipment Fault": {'req': False, 'type': FT.boolean},
        "Plants": {'req': True, 'type': FT.integer,
                   'min': 0, 'max': 20},
        "Blossoms": {'req': True, 'type': FT.integer,
                     'min': 0, 'max': 1000},
        "Fruit": {'req': True, 'type': FT.integer,
                  'min': 0, 'max': 1000},
        "Min height": {'req': True, 'type': FT.decimal,
                       'min': 0, 'max': 1000, 'inc': .01},
        "Max height": {'req': True, 'type': FT.decimal,
                       'min': 0, 'max': 1000, 'inc': .01},
        "Median height": {'req': True, 'type': FT.decimal,
                          'min': 0, 'max': 1000, 'inc': .01},
        "Notes": {'req': False, 'type': FT.long_string}
    }

    def __init__(self,filename):
        self.filename=filename

    def save_record(self,data,rownum=None):
        if rownum is not None:
            records=self.get_all_records()
            records[rownum]=data
            with open(self.filename,'w')as fh:
                csvwriter = csv.DictWriter(fh, fieldnames=self.fields.keys())
                csvwriter.writeheader()
                csvwriter.writerow(records)
        else:
            newfile = not os.path.exists(self.filename)
            with open(self.filename, 'a') as fh:
                csvwriter = csv.DictWriter(fh, fieldnames=self.fields.keys())
                if newfile:
                    csvwriter.writeheader()
                csvwriter.writerow(data)

    def get_all_records(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename,'r')as fh:
            csvreader=csv.DictReader(fh)
            missing_fields=(set(self.fields.keys())-set(csvreader.fieldnames))
            if len(missing_fields)>0:
                raise Exception(
                    "File is missing fields: {}"
                    .format(', '.join(missing_fields))
                )
            else:
                records=list(csvreader)

            trues=('true','yes','1')
            bool_fields=[
                key for key ,meta in self.fields.items()
                if meta['type']==FT.boolean
            ]
            for record in records:
                for key in bool_fields:
                    record[key]=record[key].lower()in trues
            return records

    def get_record(self,rownum):
        return self.get_all_records()[rownum]


class SettingModel:
    variables={
        'autofill date':{'type':'bool','value':True},
        'autofill sheet data':{'type':'bool','value':True}
    }

    def __init__(self,filename='abq_settings.json',path='.\\'):# 保存在当前项目路径下，如需保存在子文件内需指明路径
        self.filepath=os.path.join(os.path.expanduser(path),filename)
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath,'r')as fh:
            raw_values=json.loads(fh.read())
        # 不直接赋值给变量，防止出错
        for key in self.variables:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value=raw_values[key]['value']
                self.variables[key]['value']=raw_value

    def save(self,settings=None):
        json_string=json.dumps(self.variables)
        with open(self.filepath,'w')as fh:
            fh.write(json_string)

    def set(self,key,value):
        if (key in self.variables and type(value).__name__==self.variables[key]['type']):
            self.variables[key]['value']=value
        else:
            raise ValueError('Bad key or wrong variable type')