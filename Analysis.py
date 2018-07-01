# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 15:04:27 2018

@author: 25008
"""

import os 
import csv
import re
import numpy as np
import pandas as pd
import jieba
import jieba.posseg
from bs4 import BeautifulSoup




def read_train():
    path = 'D:/Tianchi/data/FDDC_announcements_round1_train_result_20180616/hetong.train'
    file = open(path, 'r', encoding = 'utf-8-sig')
    hetong_train = csv.reader(file, delimiter = '\t')
    hetong_train = list(hetong_train)
    file.close()
    hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    return (hetong_train)


def parta_ana(hetong_train):
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df_partya = pd.DataFrame(columns = ['公告id', '甲方', '乙方', '分句', '词性', 'Section', 'title'])
    ggid = []
    partya = []
    partyb = []
    sentence = []
    cixing = []
    section = []
    title = []
    for i in range(len(hetong_train)):
        filename = hetong_train.iloc[i,0]
        print(filename)
        try:
            htmlf = open(path + str(filename) + '.html', 'r', encoding = 'utf-8')
            htmlcont = htmlf.read()
            htmlf.close()
            soup = BeautifulSoup(htmlcont,'lxml')
        except FileNotFoundError:
            print('Fail')
            continue
        #soupcontent = re.sub('<.+>', '', str(soup))
        #soupcontent = re.sub('\n|\s', '。。', soupcontent)
        
        if hetong_train.iloc[i,1] != '':
            div = soup.findAll('div')
            k = 0
            for line in div[1:]:
                k = k + 1
                subsentence = []
                subcixing = []
                subsection = []
                subtitle = []
                if line.get('id') or line.get('title'):
                    # ob = re.findall('\w*\s?' + hetong_train.iloc[i,1] + '\w*\s?', re.sub('<.+>|\n|\s', '', str(line)))
                    strline = re.sub('<.+>|\n|   ', '', str(line))
                    ob_loc = [i.start() for i in re.finditer(hetong_train.iloc[i,1], strline)]
                    ob = [strline[max(0, j-20) : min(len(strline)-1, j+40)] for j in ob_loc]
                    for j in ob:
                        seg = jieba.posseg.cut(j)
                        st = []
                        cx = []
                        for kk in seg:
                            st.append(kk.word)
                            cx.append(kk.flag)
                        subsentence.append('/'.join(st))
                        subcixing.append('/'.join(cx))
                        subsection.append(line.get('id'))
                        subtitle.append(line.get('title'))
                    ###### 
                    _ = [ggid.append(hetong_train.iloc[i,0]) for x in subsentence]
                    _ = [partya.append(hetong_train.iloc[i,1]) for x in subsentence]
                    _ = [partyb.append(hetong_train.iloc[i,2]) for x in subsentence]
                    _ = [sentence.append(x) for x in subsentence]
                    _ = [cixing.append(x) for x in subcixing]
                    _ = [section.append(x) for x in subsection]
                    _ = [title.append(x) for x in subtitle]                
    df_partya['公告id'] = ggid
    df_partya['甲方'] = partya
    df_partya['乙方'] = partyb
    df_partya['分句'] = sentence
    df_partya['词性'] = cixing
    df_partya['Section'] = section
    df_partya['title'] = title
    writer = pd.ExcelWriter('partya.xlsx')
    df_partya.to_excel(writer, 'page_1', float_format = '%.5f', index = False, encoding = 'gbk')
    writer.save()
    
    
def partb_ana(hetong_train):
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df_partyb = pd.DataFrame(columns = ['公告id', '乙方', '句子', 'Section', 'title'])
    ggid = []
    partyb = []
    sentence = []
    section = []
    title = []
    for i in range(len(hetong_train)):
        filename = hetong_train.iloc[i,0]
        print(filename)
        try:
            htmlf = open(path + str(filename) + '.html', 'r', encoding = 'utf-8')
            htmlcont = htmlf.read()
            htmlf.close()
            soup = BeautifulSoup(htmlcont,'lxml')
        except FileNotFoundError:
            print('Fail')
            continue
        #soupcontent = re.sub('<.+>', '', str(soup))
        #soupcontent = re.sub('\n|\s', '。。', soupcontent)
        
        if hetong_train.iloc[i,2] != '':
            div = soup.findAll('div')
            k = 0
            for line in div[1:]:
                k = k + 1
                subsentence = []
                subsection = []
                subtitle = []
                if line.get('id') or line.get('title'):
                    # ob = re.findall('\w*\s?' + hetong_train.iloc[i,1] + '\w*\s?', re.sub('<.+>|\n|\s', '', str(line)))
                    strline = re.sub('<.+>|\n|\s', '', str(line))
                    ob_loc = [i.start() for i in re.finditer(hetong_train.iloc[i,2], strline)]
                    ob = [strline[max(0, j-20) : min(len(strline)-1, j+20)] for j in ob_loc]
                    _ = [subsentence.append(x) for x in ob]
                    _ = [subsection.append(line.get('id')) for x in ob]
                    _ = [subtitle.append(line.get('title')) for x in ob]
                    ###### 
                    _ = [ggid.append(hetong_train.iloc[i,0]) for x in subsentence]
                    _ = [partyb.append(hetong_train.iloc[i,2]) for x in subsentence]
                    _ = [sentence.append(x) for x in subsentence]
                    _ = [section.append(x) for x in subsection]
                    _ = [title.append(x) for x in subtitle]                
    df_partyb['公告id'] = ggid
    df_partyb['乙方'] = partyb
    df_partyb['句子'] = sentence
    df_partyb['Section'] = section
    df_partyb['title'] = title
    writer = pd.ExcelWriter('partyb.xlsx')
    df_partyb.to_excel(writer, 'page_1', float_format = '%.5f', index = False, encoding = 'gbk')
    writer.save()
    
def partproject_ana(hetong_train):
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df_partyproject = pd.DataFrame(columns = ['公告id', '甲方', '乙方', '项目名称', '句子', 'Section', 'title'])
    ggid = []
    partya = []
    partyb = []
    partyproject = []
    sentence = []
    section = []
    title = []
    for i in range(len(hetong_train)):
        filename = hetong_train.iloc[i,0]
        print(i)
        #print(filename)
        try:
            htmlf = open(path + str(filename) + '.html', 'r', encoding = 'utf-8')
            htmlcont = htmlf.read()
            htmlf.close()
            soup = BeautifulSoup(htmlcont,'lxml')
        except FileNotFoundError:
            print('Fail')
            continue
        #soupcontent = re.sub('<.+>', '', str(soup))
        #soupcontent = re.sub('\n|\s', '。。', soupcontent)
        
        if hetong_train.iloc[i,3] != '':
            div = soup.findAll('div')
            k = 0
            for line in div[1:]:
                k = k + 1
                subsentence = []
                subsection = []
                subtitle = []
                if line.get('id') or line.get('title'):
                    # ob = re.findall('\w*\s?' + hetong_train.iloc[i,1] + '\w*\s?', re.sub('<.+>|\n|\s', '', str(line)))
                    strline = re.sub('<.+>|\n|\s', '', str(line))
                    pat = re.sub('\(', '\(', hetong_train.iloc[i,3])
                    pat = re.sub('\)', '\)', pat)
                    pat= re.sub('\[', '\[', pat)
                    pat = re.sub('\]', '\]', pat)
                    ob_loc = [i.start() for i in re.finditer(pat, strline)]
                    ob = [strline[max(0, j-20) : min(len(strline)-1, j+60)] for j in ob_loc]
                    _ = [subsentence.append(x) for x in ob]
                    _ = [subsection.append(line.get('id')) for x in ob]
                    _ = [subtitle.append(line.get('title')) for x in ob]
                    ###### 
                    _ = [ggid.append(hetong_train.iloc[i,0]) for x in subsentence]
                    _ = [partya.append(hetong_train.iloc[i,1]) for x in subsentence]
                    _ = [partyb.append(hetong_train.iloc[i,2]) for x in subsentence]
                    _ = [partyproject.append(hetong_train.iloc[i,3]) for x in subsentence]
                    _ = [sentence.append(x) for x in subsentence]
                    _ = [section.append(x) for x in subsection]
                    _ = [title.append(x) for x in subtitle]                
    df_partyproject['公告id'] = ggid
    df_partyproject['甲方'] = partya
    df_partyproject['乙方'] = partyb
    df_partyproject['项目名称'] = partyproject
    df_partyproject['句子'] = sentence
    df_partyproject['Section'] = section
    df_partyproject['title'] = title
    writer = pd.ExcelWriter('partyproject.xlsx')
    df_partyproject.to_excel(writer, 'page_1', float_format = '%.5f', index = False, encoding = 'gbk')
    writer.save()
    
def execute():
    datatrain = read_train()
    #parta_ana(datatrain)
    #partb_ana(datatrain)
    partproject_ana(datatrain)


        
if __name__ == '__main__':
    execute()
    