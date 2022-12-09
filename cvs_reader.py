import numpy as np
import csv
import pandas as pd
import json

class DataTools:
    def __init__(self, ad_data = None, abs_data = None, comp_dups = [], one_offs = []):
        self.ad_data = ad_data
        self.abs_data = abs_data
        self.comp_dups = comp_dups
        self.one_offs = one_offs

    def get_ad_data(self):
        with open(r"file_output\ad_computers.csv", 'r') as f:
            self.ad_data = list(csv.DictReader(f))

    def get_abs_data(self):
        with open(r"file_output\abs_computers.csv", 'r') as f:
            self.abs_data = list(csv.DictReader(f))

    def dup_check(self):
        abs_name_list = []
        for abs_name in self.abs_data:
            abs_name_list.append(abs_name.get("deviceName"))
        for ad_name in self.ad_data:
            if ad_name.get("name") in abs_name_list:
                self.comp_dups.append((ad_name.get("name")))
            else:
                self.one_offs.append(ad_name)
        print(len(self.comp_dups))
        print(len(self.one_offs))



data_tool = DataTools()


data_tool.get_abs_data()
data_tool.get_ad_data()
data_tool.dup_check()

