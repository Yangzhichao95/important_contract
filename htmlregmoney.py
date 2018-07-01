# -*- coding: utf-8 -*-
# 0.7105
"""
Created on Thu Jun 21 09:38:18 2018

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
        return(partyb)
    else:
        lb = [re.sub('\d+', '', x) for x in lb]
        # Change the parenthesis
    return (lb)

def transfer_up_low(str_money):
    up_low = [x.group() for x in re.finditer('((\d*)(，|,)?)*(\d+)(\.?)(\d*)', str_money)]
    up_money = up_low[0]
    low_money = up_low[1]
    unit = re.search('亿|千万|百万|十万|万|千|百|十|元', str_money).group()
    return (transfer(up_money + unit), transfer(low_money + unit))    
    
def transfer(str_money):
    money = re.search('((\d*)(，|,)?)*(\d+)(\.?)(\d*)', str_money).group()
    money = float(re.sub('，|,', '', money))
    unit = re.search('亿|千万|百万|十万|万|千|百|十|元', str_money).group()
    if re.search('\.(\d*)', str(money)):
        num_decimal = len(re.search('\.(\d*)', str(money)).group(1))
    else:
        num_decimal = 0
    if unit == '亿':
        return (round(money*100000000, max(num_decimal-8, 0)))
    elif unit == '千万':
        return (round(money*10000000, max(num_decimal-7, 0)))
    elif unit == '百万':
        return (round(money*1000000, max(num_decimal-6, 0)))
    elif unit == '十万':
        return (round(money*100000, max(num_decimal-5, 0)))
    elif unit == '万':
        return (round(money*10000, max(num_decimal-4, 0)))
    elif unit == '千':
        return (round(money*1000, max(num_decimal-3, 0)))
    elif unit == '百':
        return (round(money*100, max(num_decimal-2, 0)))
    elif unit == '十':
        return (round(money*10, max(num_decimal-1, 0)))
    else:
        return (money)
    
    
def threshold_money(money):
    if money < 5000:
        return ''
    else:
        return(money)
    
def match_money(soup):
    # The return can be a str('') or a float(int) or a list(more than one results)
    #pat_up_low_foreign = '\d[\d|，|,|\.|—|-|~|\s]+(亿|千万|百万|十万|万|千|百|十)?\w?元'
    pat_up_low_foreign = '((\d*)(，|,)?)*(\d+)(\.?)(\d*) *(—|\-|~)((\d*)(，|,)?)*(\d+)\.?(\d*) *(亿|千万|百万|十万|万|千|百|十)?\w?元'
    #pat_up_low = '\d[\d|，|,|\.|—|-|~|\s]+(亿|千万|百万|十万|万|千|百|十)?元'
    pat_up_low = '((\d*)(，|,)?)*(\d+)(\.?)(\d*) *(—|\-|~)((\d*)(，|,)?)*(\d+)\.?(\d*) *(亿|千万|百万|十万|万|千|百|十)?元'
    #pat_foreign ='\d[\d|，|,|\.|\s]+(亿|千万|百万|十万|万|千|百|十)?\w?元'
    pat_foreign = '((\d*)(，|,)?)*(\d+)(\.?)(\d*) *(亿|千万|百万|十万|万|千|百|十)?\w?元'
    #pat_money ='\d[\d|，|,|\.|\s]+(亿|千万|百万|十万|万|千|百|十)?元'
    pat_money = '((\d*)(，|,)?)*(\d+)(\.?)(\d*) *(亿|千万|百万|十万|万|千|百|十)?元'
    soupcontent = re.sub('<.+>|\n|   ', '', str(soup)) # Very important
    while re.search('<.+?>', soupcontent):
        soupcontent = re.sub('<.+?>', '', soupcontent)
    soupcontent = re.sub('=\d+', '', soupcontent) # For 250247.html
    section1 = str(soup.find(id = 'SectionCode_1'))
    section1 = re.sub('<.+>|\n|   ', '', section1)
    while re.search('<.+?>', section1):
        section1 = re.sub('<.+?>', '', section1)
    section1 = re.sub('=\d+', '', section1) # For 250247.html
    # 1 Match the money with different upper and lower limit.
    # Only match the first pattern in the content
    if re.search(pat_up_low_foreign, soupcontent):
        if re.search(pat_up_low, soupcontent):
            up_low_raw =  re.search(pat_up_low, soupcontent).group()
            up_money, low_money = transfer_up_low(up_low_raw)
        else:
            up_low_raw =  re.search(pat_up_low_foreign, soupcontent).group()
            up_money, low_money = transfer_up_low(up_low_raw)
        return (up_money, low_money)
    # 2 Match the money with the same upper and lower limit
    # According to the number of partyb, we confirm the number of  money we should get
    partyb = match_partyb(soup)
    if type(partyb) is str or len(partyb) == 1:
        loc = [x.start() for x in re.finditer(pat_money, section1)]
        if len(loc) == 0:
            loc = [x.start() for x in re.finditer(pat_foreign, section1)]
        if len(loc) > 1:
            money = [section1[max(0,j-10):min(len(section1), j+20)] for j in loc]
            moneycopy = money.copy()
            for sub_money in moneycopy:
                if re.search('资本|资产|收入|利润|合计|总共', sub_money):
                    money.remove(sub_money)
                    continue
                if re.search('((中标|合同)总?(金额|价))|：', sub_money[0:10]):
                    raw_return = transfer(re.search(pat_foreign, sub_money).group())
                    return(threshold_money(raw_return), threshold_money(raw_return))
            money = [re.search(pat_foreign, x).group() for x in money if re.search(pat_foreign, x)]
            if len(money) == 0:
                return('','')
            money = max([transfer(x) for x in money])
            # Set a threshold for the number of money
            return (threshold_money(money), threshold_money(money))
        elif len(loc) == 1:
            money = section1[max(0,loc[0]-10):min(len(section1), loc[0]+20)]
            if re.search('资本|资产|收入|利润|合计|总共', money):
                return('', '')
            money = transfer(re.search(pat_foreign, money).group())
            return (threshold_money(money), threshold_money(money))
        else:
            loc = [x.start() for x in re.finditer(pat_money, soupcontent)]
            if len(loc) == 0:
                loc = [x.start() for x in re.finditer(pat_foreign, soupcontent)]
            if len(loc) > 1:
                money = [soupcontent[max(0,j-10):min(len(soupcontent), j+20)] for j in loc]
                moneycopy = money.copy()
                for sub_money in moneycopy:
                    if re.search('资本|资产|收入|利润|合计|总共', sub_money):
                        money.remove(sub_money)
                        continue
                    if re.search('((中标|合同)总?(金额|价))|：', sub_money[0:10]):
                        raw_return = transfer(re.search(pat_foreign, sub_money).group())
                        return(threshold_money(raw_return), threshold_money(raw_return))
                money = [re.search(pat_foreign, x).group() for x in money if re.search(pat_foreign, x)]
                if len(money) == 0:
                    return('','')
                money = max([transfer(x) for x in money])
                return (threshold_money(money), threshold_money(money))
            
            elif len(loc) == 1:
                money = soupcontent[max(0,loc[0]-8):min(len(soupcontent), loc[0]+20)]
                if re.search('资本|资产|收入|利润|合计|总共', money):
                    return('', '')
                money = transfer(re.search(pat_foreign, money).group())
                return (threshold_money(money), threshold_money(money))
            else:
                return ('', '')
    else:
        money = []
        for sub_partyb in partyb:
            loc = [x.start() for x in re.finditer(sub_partyb, soupcontent)]
            subcontent = [soupcontent[max(0,j):min(len(soupcontent), j+150)] for j in loc]
            # Only find the first
            submoney = [re.search(pat_foreign, x).group() for x in subcontent if re.search(pat_foreign, x)]
            if len(submoney) == 0:
                money.append('')
            else:
                money.append(max([threshold_money(transfer(x)) for x in submoney]))
        return (money, money)
            

def execute():
    file = open('D:/Tianchi/data/round1_train_20180518/重大合同/hetong.train', 'r', encoding = 'utf-8-sig')
    hetong_train = csv.reader(file, delimiter = '\t')
    hetong_train = list(hetong_train)
    file.close()
    hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df = pd.DataFrame(columns = ['公告id', '合同金额上限', '合同金额下限'])
    i = 0
    lst = []
    #lst_int = []
    for i in os.listdir(path):
        #lst_int.append(int(i.replace('.html', '')))
        lst.append(i)
    #df['公告id'] = lst_int
    ggid = []
    up_money_all = []
    low_money_all = []
    for filename in lst:
        print(filename)
        htmlf = open(path + filename, 'r', encoding = 'utf-8')
        htmlcont = htmlf.read()
        htmlf.close()
        soup = BeautifulSoup(htmlcont,'lxml')
        
        ##################################################
        up_money, low_money = match_money(soup)
        if type(up_money) is float or type(up_money) is int:
            ggid.append(int(filename.replace('.html', '')))
            up_money_all.append(up_money)
            low_money_all.append(low_money)
            print(up_money)
            #time.sleep(0.1)
        else:
            if type(up_money) is str:
                ggid.append(int(filename.replace('.html', '')))
                up_money_all.append('')
                low_money_all.append('')
            else:
                for i in range(len(up_money)):
                    ggid.append(int(filename.replace('.html', '')))
                    up_money_all.append(up_money[i])
                    low_money_all.append(low_money[i])
                    print(up_money[i])
                    #time.sleep(0.1)
        ################################################
    df['公告id'] = ggid
    df['合同金额上限'] = up_money_all
    df['合同金额下限'] = low_money_all
    writer = pd.ExcelWriter('Save_money.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()
    

if __name__ == '__main__':
    execute()