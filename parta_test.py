# -*- coding: utf-8 -*-
# 统计出训练数据中所有甲方的，并计算测试数据中有多少公告中出现了训练数据中出现的甲方
"""
Created on Tue Jun 19 22:21:58 2018

@author: 25008
"""

import pandas as pd
from bs4 import BeautifulSoup
import os 
import csv
import re
import jieba
import jieba.posseg

file = open('D:/Tianchi/data/round1_train_20180518/重大合同/hetong.train', 'r', encoding = 'utf-8-sig')
hetong_train = csv.reader(file, delimiter = '\t')
hetong_train = list(hetong_train)
file.close()
hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])

partya_list = list(set(hetong_train['甲方']))
partya_list.pop(0)

path = 'D:/Tianchi/data/FDDC_announcements_round1_test_a_20180605/重大合同/html/'
pat_partyb = '(\w+|\w+(（\w*）|\(\w*\))\w*)(公司|局|业|院|委|室|部|中心|银行)'
lst = []
#lst_int = []
for i in os.listdir(path):
    #lst_int.append(int(i.replace('.html', '')))
    lst.append(i)
count = 0
for filename in lst:
    htmlf = open(path + filename, 'r', encoding = 'utf-8')
    htmlcont = htmlf.read()
    htmlf.close()
    soup = BeautifulSoup(htmlcont,'lxml')
    soupcontent = re.sub('<.+>|\n|   ', '', str(soup))
    soupcontent = soupcontent.replace('本公司', '')
    soupcontent = soupcontent.replace('子公司', '')
    la_raw = re.findall(pat_partyb, soupcontent)
    la_raw = [''.join(x) for x in la_raw]
    for i in range(len(partya_list)):
        if partya_list[i] in la_raw:
            count = count + 1
            print(filename + 'html')
            break
print(count)



    