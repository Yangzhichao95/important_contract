# -*- coding: utf-8 -*-
#### 找主键
"""
Created on Wed Jun 20 10:58:56 2018

@author: 25008
"""

import re
import os
import time
import pandas as pd
import jieba
import jieba.posseg
from bs4 import BeautifulSoup

pat_partyb = '(\w+|\w+(（\w*）|\(\w*\))\w*)'




def execute():
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df = pd.DataFrame(columns = ['公告id', '甲方', '乙方'])
    i = 0
    lst = []
    #lst_int = []
    for i in os.listdir(path):
        #lst_int.append(int(i.replace('.html', '')))
        lst.append(i)
    #df['公告id'] = lst_int
    ggid = []
    partyb_all = []
    for filename in lst:
        htmlf = open(path + filename, 'r', encoding = 'utf-8')
        htmlcont = htmlf.read()
        htmlf.close()
        soup = BeautifulSoup(htmlcont,'lxml')
        partyb = match_partyb(soup, pat_partyb)
        #df.loc[df['公告id'] == int(filename.replace('.html', '')), '乙方'] = partyb
        if type(partyb) is str:
            ggid.append(int(filename.replace('.html', '')))
            partyb_all.append(partyb)
            print(filename)
            print(partyb)
            # time.sleep(0.1)
        else:
            if len(partyb) == 0:
                ggid.append(int(filename.replace('.html', '')))
                partyb_all.append('')
            else:
                for i in range(len(partyb)):
                    ggid.append(int(filename.replace('.html', '')))
                    partyb_all.append(partyb[i])
                    print(filename)
                    print(partyb[i])
                    #time.sleep(0.1)
    df['公告id'] = ggid
    df['乙方'] = partyb_all
    writer = pd.ExcelWriter('Save_partyb.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()

if __name__ == '__main__':
    execute()