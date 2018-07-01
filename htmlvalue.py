# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 09:47:16 2018

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

def match_value(soup, Company):
    div = soup.findAll('div')
    div_0 = div[0]
    title = re.sub('\*', '\*', div_0.get('title'))
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    ## 找出公司全称
    if re.search('(\d+)?([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])):
        if re.search('号([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])):
            name = re.search('号([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])).group(1)
        else:
            name = re.search('(\d+)?([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])).group(2)
        if name[0] == '一' or name[0] == '号':
            # 因格式问题造成的在开头或结尾可能多出一个一
            full_name = name[1:]
        elif name[len(name)-1] == '一':
            full_name = name[1:(len(name)-1)]
        else:
            full_name = name
    elif re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:120]):
        name = re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:120]).group(3)
        full_name = search_company(name, Company)
    else:
        full_name = search_company(div_0.get('title')[0:4], Company)
    # 初始化各个返回值
    partya = []
    partyb = []
    project = []
    contract = []
    money_up = []
    money_low = []
    combo = []
    # 寻找Key
    partya_partyb_combo = match_key(soup, Company)
    for i in partya_partyb_combo:
        partya.append(i[0])
        partyb.append(i[1])
        combo.append(i[2])
    if len(partyb) == 0:
        # 如果没找到乙方，则返回空
        return(zip(partya, partyb, project, contract, money_up, money_low))
    elif
        


def execute():
    file = open('D:/Tianchi/data/round1_train_20180518/重大合同/hetong.train', 'r', encoding = 'utf-8-sig')
    hetong_train = csv.reader(file, delimiter = '\t')
    hetong_train = list(hetong_train)
    file.close()
    hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    f = open('D:/Tianchi/data/FDDC_announcements_company_name_20180531.json','r',encoding="utf-8")
    Company = json.load(f)
    df = pd.DataFrame(columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    i = 0
    lst = []
    #lst_int = []
    for i in os.listdir(path):
        #lst_int.append(int(i.replace('.html', '')))
        lst.append(i)
    #df['公告id'] = lst_int
    ggid = []
    partya_all = []
    partyb_all = []
    project_all = []
    contract_all = []
    money_up_all = []
    money_low_all = []
    combo_all = []
    for filename in lst:
        htmlf = open(path + filename, 'r', encoding = 'utf-8')
        htmlcont = htmlf.read()
        htmlf.close()
        soup = BeautifulSoup(htmlcont,'lxml')
        print(filename)
        key_value = match_value(soup, Company)
        for i in key_value:
            ggid.append(int(filename.replace('.html', '')))
            partya_all.append(i[0])
            partyb_all.append(i[1])
            project_all.append(i[2])
            contract_all.append(i[3])
            money_up_all.append(i[4])
            money_low_all.append(i[5])
            combo_all.append(i[6])
            #print(i)
            #time.sleep(0.1)
    df['公告id'] = ggid
    df['甲方'] = partya_all
    df['乙方'] = partyb_all
    df['项目名称'] = project_all
    df['合同名称'] = contract_all
    df['合同金额上限'] = money_up_all
    df['合同金额下限'] = money_low_all
    df['联合体成员'] = combo_all
    writer = pd.ExcelWriter('Save_key_value.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()
    

if __name__ == '__main__':
    execute()