# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 12:31:14 2018

@author: 25008
"""

import pandas as pd
import re 
from bs4 import BeautifulSoup
import jieba
import jieba.posseg

path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html'
# Match partyb
pat_partyb = '(\w*?|\w*?(（\w*）|\(\w*\))\w*?)(公司|业|局|院|委|室|部|中心|行)'
# Match money
pat_money = '(\w+\d+)\.?(\d*)(亿\千万\百万\万\千\百\十)?元'
# Match parta

# Match money_max

# Match money_min

# Match consortium member

htmlf = open(path + '/2515.html', 'r', encoding = 'utf-8')
htmlfcont = htmlf.read()
htmlf.close()

soup = BeautifulSoup(htmlfcont, 'lxml')
soupcontent = re.sub('<.+>|\n|   ', '', str(soup))
soupcontent = soupcontent.replace('本公司', '')
soupcontent = soupcontent.replace('子公司', '')
section1 = str(soup.find(id = 'SectionCode_1'))
section1 = re.sub('<.+>|\n', '', section1)
re.search(pat_partyb, section1).group()

ls = re.findall('(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司|业|局|院|委|室|部|中心|行)', soupcontent)
ls = [''.join(x) for x in ls]


seg = jieba.posseg.cut(partya_raw) 
l = []
s = [] 
for i in seg: 
    l.append(i.word)
    s.append(i.flag)
    
###############################################################################
import json
f = open('D:/Tianchi/data/FDDC_announcements_company_name_20180531.json','r',encoding="utf-8")
Company = json.load(f)
secShortName = [x['secShortName'] for x in Company['data']]
secFullName = [x['secFullName'] for x in Company['data']]
secShortNameChg = [x['secShortNameChg'] for x in Company['data'] if len(x) is 3 ]
path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
i = 0
lst = []
for i in os.listdir(path):
    #lst_int.append(int(i.replace('.html', '')))
    lst.append(i)

######### For train
name = []
k = []
i = 0
for filename in lst:
    print(i)
    htmlf = open(path + filename, 'r', encoding = 'utf-8')
    htmlcont = htmlf.read()
    htmlf.close()
    soup = BeautifulSoup(htmlcont,'lxml')
    div = soup.findAll('div')[0]
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    if re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:100]):
        name.append(re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:100]).group(3))
    elif re.search('([\d|\s]+)?([\w|\（|\）]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', div.get('title')), re.sub('“|”', '', soupcontent[0:100])):
        # 中标公告（一） 中标公告（二）
        name.append(re.search('([\d|\s]+)?([\w|\（|\）]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', div.get('title')), re.sub('“|”', '', soupcontent[0:100])).group(2))
        k.append(re.search('([\d|\s]+)?([\w|\（|\）]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', div.get('title')), re.sub('“|”', '', soupcontent[0:100])).group(2))
    else:
        name.append(div.get('title')[0:4])
    i = i + 1

##
k = 0
extra = []
for x in name:
    tag = 1
    if x in secShortName or x in secFullName or x[0:4] in secShortName:
        k = k + 1
        continue
    for y in secShortNameChg:
        if x in y or x[0:4] in y:
            k = k + 1
            tag = 0
            break
    if tag:
        extra.append(x)
########## For test
path = 'D:/Tianchi/data/FDDC_announcements_round1_test_a_20180605/重大合同/html/'
i = 0
lst = []
for i in os.listdir(path):
    #lst_int.append(int(i.replace('.html', '')))
    lst.append(i)
name = []
k = []
i = 0
for filename in lst:
    print(i)
    htmlf = open(path + filename, 'r', encoding = 'utf-8')
    htmlcont = htmlf.read()
    htmlf.close()
    soup = BeautifulSoup(htmlcont,'lxml')
    div = soup.findAll('div')[0]
    soupcontent = re.sub('<.+>|\n | ', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    if re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:100]):
        name.append(re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:100]).group(3))
    elif re.search('([\d|\s]+)?([\w|\（|\）]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', div.get('title')), re.sub('“|”', '', soupcontent[0:100])):
        # 中标公告（一） 中标公告（二）
        name.append(re.search('([\d|\s]+)?([\w|\（|\）]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', div.get('title')), re.sub('“|”', '', soupcontent[0:100])).group(2))
    else:
        name.append(div.get('title')[0:4])
        k.append(div.get('title')[0:4])
    i = i + 1

##
k = 0
extra = []
for x in hetong_train['甲方']:
    tag = 1
    if x in secShortName or x in secFullName or x[0:4] in secShortName:
        k = k + 1
        continue
    for y in secShortNameChg:
        if x in y or x[0:4] in y:
            k = k + 1
            tag = 0
            break
    if tag:
        extra.append(x)