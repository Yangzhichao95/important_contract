# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 09:47:28 2018

@author: 25008
"""
import re
import os
import time
import pandas as pd
from bs4 import BeautifulSoup
import jieba
import jieba.posseg
import csv
import json
from Function_all import *
from Function_temp import *


def execute():
    f = open('D:/Tianchi/data/FDDC_announcements_company_name_20180531.json','r',encoding="utf-8")
    Company = json.load(f)
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    filename = '81821.html'
    htmlf = open(path + filename, 'r', encoding = 'utf-8')
    htmlcont = htmlf.read()
    htmlf.close()
    soup = BeautifulSoup(htmlcont,'lxml')
    print(filename)
    key_value = match_value(soup, Company)
    for i in key_value_combo:
        print(i)

    

if __name__ == '__main__':
    execute()