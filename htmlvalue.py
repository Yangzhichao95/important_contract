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

def match_value(soup, Company):
    full_name = find_full_name(soup, Company)
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
        return(zip(partya, partyb, project, contract, money_up, money_low, combo))
    elif full_name[0:4] == '中国铁建' and len(partyb) > 1:
        key_value = tiejian_key_value(soup) 
        return(key_value)
    elif (full_name[0:4] == '中国北车' or full_name[0:4] == '中国中车' or full_name[0:4] == '中国南车') and len(partyb) > 1:
        key_value = beiche_key_value(soup, full_name)
        return(key_value)
    else:
        contract_result = find_contract(soup)
        contract.append(contract_result)
        project.append(find_project(soup, contract_result))
        up_money, low_money = find_money(soup)
        money_up.append(up_money)
        money_low.append(low_money)
        return(zip(partya, partyb, project, contract, money_up, money_low, combo))
        

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
    # path = 'D:/Tianchi/data/FDDC_announcements_round1_test_a_20180605/重大合同/html/'
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
    df['甲方'] = refine_output_partya(partya_all)
    df['乙方'] = refine_output_partyb(partyb_all)
    df['项目名称'] = refine_output_project(project_all)
    df['合同名称'] = refine_output_contract(contract_all)
    df['合同金额上限'] = money_up_all
    df['合同金额下限'] = money_low_all
    df['联合体成员'] = refine_output_partyb(combo_all)
    #writer = pd.ExcelWriter('D:/Tianchi\data/Save_key_value.xlsx')
    writer = pd.ExcelWriter('Save_key_value.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()
    

if __name__ == '__main__':
    execute()