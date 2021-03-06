# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 14:42:44 2018

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
from Function import *


def match_key(soup, Company):
    full_name = find_full_name(soup, Company)
    # 对于中国铁建和中国北车的公告
    if full_name[0:4] == '中国铁建':
        key = tiejian_key(soup)
        if type(key) is zip:
            return(key)
    if full_name[0:4] == '中国北车' or full_name[0:4] == '中国中车' or full_name[0:4] == '中国南车':
        key = beiche_key(soup, full_name)
        if type(key) is zip:
            return(key)
    soupcontent = re.sub('<.+>|\n | ', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    div = soup.findAll('div')
    partya = []
    partyb = []
    combo = []
    # 先找乙方关键词
    # 甲方结尾可为(公司|局|院|馆|委员会|集团|室|部|中心|银行|[A-Za-z|\-]+)
    soupcontent = re.sub('本公司|我公司|占公司|对公司|是公司|影响公司|为公司|项目公司|后公司|提升公司|上述公司|及公司', '', soupcontent)
    lb = find_partyb(full_name, soupcontent)
    soupcontent = re.sub('控股子公司|子公司', '', soupcontent)
    if len(lb) <= 1:
        # 如果只有一个或者没有子公司，即一个乙方
        if len(lb) == 0:
            partyb.append(full_name)
        else:
            partyb.append(lb[0])
        if re.search('联合体|联合中标|分别收到|丙方|共同', soupcontent):
            # 如果联合体存在
            content_split = re.split('\n|，|。', soupcontent)
            content_split = [x for x in content_split if len(x) > 0]
            for content in content_split:
                if re.search('联合体成员：', content):
                    combo_raw = re.search('联合体成员：([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', content)
                    combo.append(combo_raw.group(1) + combo_raw.group(2))
                    break
                if re.search('联合体|联合中标|分别收到|丙方|共同', content):
                    loc = content.index(re.search('联合体|联合中标|分别收到|丙方|共同', content).group())
                    combo_raw = re.findall('(与|和|、)([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', content[:loc])
                    combo_raw = [x[1] + x[2] for x in combo_raw]
                    combo_raw = [x for x in combo_raw if len(x) > 5]
                    combo.append('、'.join(combo_raw))
                    break
        if len(combo) == 0:
            combo.append('')
        pat_temp = partyb[0] + '|' + full_name + '|' + re.sub('、', '|', combo[0])
        pat_temp = re.sub('\(', '\(', pat_temp)
        pat_temp = re.sub('\)', '\)', pat_temp)
        soupcontent = re.sub(pat_temp, '', soupcontent)
        #寻找甲方
        result_a = find_partya(soupcontent, div)
        if result_a is not None:
            partya.append(result_a)
        else:
            content_split = re.split('\n|,', soupcontent)
            #content_split = [re.sub(pat_temp, '', x) for x in content_split if len(x) > 0]
            content_split = [x for x in content_split if len(x) > 0]
            content_split = [x for x in content_split if re.search('([\w|\(|\)|（|）]+)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', x)]
            company_split = [re.search('([\w|\(|\)|（|）]+)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', x).group() for x in content_split]
            if len(company_split) == 1 and len(company_split[0]) < 6:
                partya.append('')
            elif len(company_split) == 1:
                partya_raw = company_split[0]
                seg = jieba.posseg.cut(partya_raw)
                word = []
                part = []
                for i in seg:
                    word.append(i.word)
                    part.append(i.flag)
                join_company = part_join(word.copy(), part.copy())
                if re.search('招标', join_company):
                    partya.append('')
                else:
                    partya.append(join_company)
            else:
                # 可以对以下简称在做个搜索
                dic_company = dict()
                for i in range(len(company_split)):
                    for j in range(i,len(company_split)):
                        sub_result = bottom_up_dp_lcs(company_split[i], company_split[j])
                        if re.search('公司|局|院|馆|委员会|集团|室|部|中心|银行', sub_result):
                            if sub_result in dic_company:
                                dic_company[sub_result] = dic_company[sub_result] + 1
                            else:
                                dic_company[sub_result] = 1
                if len(dic_company) == 0:
                    partya.append('')
                else:
                    for key in dic_company:
                        if len(key) < 6 or re.search('招标', key):
                            dic_company[key] = 0
                    if max(zip(dic_company.values(), dic_company.keys()))[0] == 0:
                        partya.append('')
                    else:
                        partya.append(max(dic_company, key=dic_company.get))                                
        return(zip(refine_partya_key(partya), refine_partyb_key(partyb), refine_partyb_key(combo))) 
    return(zip(refine_partya_key(partya), refine_partyb_key(partyb), refine_partyb_key(combo)))


def execute():
    file = open('D:/Tianchi/data/round1_train_20180518/重大合同/hetong.train', 'r', encoding = 'utf-8-sig')
    hetong_train = csv.reader(file, delimiter = '\t')
    hetong_train = list(hetong_train)
    file.close()
    hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    f = open('D:/Tianchi/data/FDDC_announcements_company_name_20180531.json','r',encoding="utf-8")
    Company = json.load(f)
    df = pd.DataFrame(columns = ['公告id', '甲方', '乙方', '联合体成员'])
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
    combo_all = []
    for filename in lst:
        htmlf = open(path + filename, 'r', encoding = 'utf-8')
        htmlcont = htmlf.read()
        htmlf.close()
        soup = BeautifulSoup(htmlcont,'lxml')
        print(filename)
        partya_partyb_combo = match_key(soup, Company)
        for j in partya_partyb_combo:
            ggid.append(int(filename.replace('.html', '')))
            partya_all.append(j[0])
            partyb_all.append(j[1])
            combo_all.append(j[2])
            #print(j)
            #time.sleep(0.1)
    df['公告id'] = ggid
    df['甲方'] = partya_all
    df['乙方'] = partyb_all
    df['联合体成员'] = combo_all
    writer = pd.ExcelWriter('Save_key.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()
    

if __name__ == '__main__':
    execute()