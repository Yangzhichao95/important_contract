# -*- coding: utf-8 -*-
#### 只找乙方
# 0.879
"""
Created on Fri Jun 15 11:43:19 2018

@author: 25008
"""

import re
import os
import time
import pandas as pd
from bs4 import BeautifulSoup

path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html'
# Match partyb
#pat_partyb1 = '(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司|局|业|院|委|室|部|中心|银行)'
#pat_partyb2 = '(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司|局|业|院|委|室|部|中心|银行)'
pat_partyb = '(\w+|\w+(（\w*）|\(\w*\))\w*)'
# Match money
pat_money = '(\w+\d+)\.?(\d*)(亿\千万\百万\万\千\百\十)?元'
# Match parta

# Match money_max

# Match money_min

# Match consortium member

def match_partyb(soup):
    pat_partyb = '(\w+|\w+(（\w*）|\(\w*\))\w*)'
    partyb = ''
    section1 = str(soup.find(id = 'SectionCode_1'))
    section1 = re.sub('<.+>|\n|   ', '', section1)
    section1 = section1.replace('本公司', 'bengongsi')
    lb = []
    if re.search(pat_partyb + '(公司)', section1):
        partyb = re.search(pat_partyb + '(公司)', section1).group()
    elif re.search(pat_partyb + '(局|院|委|室|部|中心|银行)', section1):
        partyb = re.search(pat_partyb + '(局|院|委|室|部|中心|银行)', section1).group()
    elif re.search('公告', section1):
        partyb = re.search('公告', section1).group()
    elif re.search(pat_partyb + '(公司|局|院|委|室|部|中心|银行)', re.sub('<.+>|\n|   ', '', str(soup))[0:80]):            
        partyb = re.search(pat_partyb + '(公司|局|院|委|室|部|中心|银行)', re.sub('<.+>|\n|   ', '', str(soup))[0:80]).group()
        
    # Subsidiary Corporation
    if re.search('子公司', section1):
        if len(re.findall('子公司(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司)', section1)):
            lb_raw = re.findall('子公司(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司)', section1)
            lb_refine = [x[0] + x[2] for x in lb_raw]
            _ = [lb.append(x) for x in list(set(lb_refine))]
        elif len(re.findall('子公司(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|委|室|部|中心|银行)', section1)):
            lb_raw = re.findall('子公司(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|委|室|部|中心|银行)', section1)
            lb_refine = [x[0] + x[2] for x in lb_raw]
            _ = [lb.append(x) for x in list(set(lb_refine))]
    
    if re.search('子公司', section1) is None or len(lb) == 0:
        soupcontent = re.sub('<.+>|\n|\s', '', str(soup)) #0.8646
        #soupcontent = re.sub('<.+>|\n|   ', '', str(soup)) #0.8631
        soupcontent = soupcontent.replace('本公司', 'bengongsi')
        
        if re.search('子公司', soupcontent):
            if len(re.findall('子公司(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司)', soupcontent)):
                lb_raw = re.findall('子公司(\w*?|\w*?(（\w*）|\(\w*\))\w*?)(公司)', soupcontent)
                # Only find one
                #lb.append(lb_raw[0][0] + lb_raw[0][2])
                # Find All
                lb_refine = [x[0] + x[2] for x in lb_raw if re.search('(和|或)', ''.join(x)) is None]
                _ = [lb.append(x) for x in list(set(lb_refine))]
            elif len(re.findall('子公司(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|委|室|部|中心|银行)', soupcontent)):
                lb_raw = re.findall('子公司(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|委|室|部|中心|银行)', soupcontent)
                # Only find one
                #lb.append(lb_raw[0][0] + lb_raw[0][2])
                # Find All
                lb_refine = [x[0] + x[2] for x in lb_raw if re.search('(和|或)', ''.join(x)) is None]
                _ = [lb.append(x) for x in list(set(lb_refine))]
    
    # Some Manipulation    
    if len(lb) == 0:
        partyb = re.sub('\d+', '', partyb)
        partyb = re.sub('（', '(', partyb)
        partyb = re.sub('）', ')', partyb)
        partyb = re.sub('\(.*\)', '', partyb)
        return(partyb)
    else:
        lb = [re.sub('\d+', '', x) for x in lb]
        # Change the parenthesis
        lb = [re.sub('（', '(', x) for x in lb]
        lb = [re.sub('）', ')', x) for x in lb]
        lb = [re.sub('\(.*\)', '', x) for x in lb]
    return (lb)
        
    

def execute():
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df = pd.DataFrame(columns = ['公告id', '乙方'])
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
        partyb = match_partyb(soup)
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
