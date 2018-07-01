# -*- coding: utf-8 -*-
#0.8257
"""
Created on Fri Jun 22 11:01:36 2018

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

def refine_contract(contract):
    contract = re.sub('&lt;', '<', contract)
    contract = re.sub('&gt;', '>', contract)
    contract = re.sub('（', '(', contract)
    contract = re.sub('）', ')', contract)
    contract = re.sub('《|》|\s|/', '', contract)
    return (contract.capitalize())
    

def match_contract(soup):
    contract = ''
    pat_contract = '《.+?》'
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    section1 = str(soup.find(id = 'SectionCode_1'))
    section1 = re.sub('<.+>|\n|\s', '', section1)
    partyb = match_partyb(soup)
    if type(partyb) is str or len(partyb) == 1:
        contract = re.findall(pat_contract, section1)
        if len(contract) > 0:
            contractcopy = contract.copy()
            for sub_contract in contractcopy:
                if re.search('议案|公告|公示|合同法|备忘录',sub_contract):
                    contract.remove(sub_contract)
                    continue
                if re.search('合同|协议|[a-zA-Z]', sub_contract) is None:
                    contract.remove(sub_contract)
            if len(contract) > 0:
                count = dict()
                for i in contract:
                    if i in count:
                        count[i] = count[i] + 1
                    else:
                        count[i] = 1
                return(refine_contract(max(count)))

        if re.findall(pat_contract, soupcontent):
            contract = re.findall(pat_contract, soupcontent)
            if len(contract) > 0:
                contractcopy = contract.copy()
                for sub_contract in contractcopy:
                    if re.search('议案|公告|公示|合同法|备忘录',sub_contract):
                        contract.remove(sub_contract)
                        continue
                    if re.search('合同|协议|[a-zA-Z]', sub_contract) is None:
                        contract.remove(sub_contract)                    
                if len(contract) > 0:
                    count = dict()
                    for i in contract:
                        if i in count:
                            count[i] = count[i] + 1
                        else:
                            count[i] = 1
                    return(refine_contract(max(count)))
        if re.search('(签订了|签署了)(\w+?)(合同|协议|合同书|协议书)', soupcontent):
            contract = re.search('(签订了|签署了)(\w+?)(合同|协议|合同书|协议书)', soupcontent).group(2) + re.search('(签订了|签署了)(\w+?)(合同|协议|合同书|协议书)', soupcontent).group(3)
            return(refine_contract(contract))
        else:
            return('')
    else:
        contract = []
        for sub_partyb in partyb:
            loc = [x.start() for x in re.finditer(sub_partyb, soupcontent)]
            subcontent = [soupcontent[max(0,j):min(len(soupcontent), j+150)] for j in loc]
            subcontract = [re.search(pat_contract, x).group() for x in subcontent if re.search(pat_contract, x)]
            if len(subcontract) == 0:
                subcontract = [re.search('(签订了|签署了)(\w+?)(合同|协议|合同书|协议书)', x).group(2) + re.search('(签订了|签署了)(\w+?)(合同|协议|合同书|协议书)', x).group(3) for x in subcontent if re.search('(签订了|签署了)(\w+?)(合同|协议|合同书|协议书)', x)]
            if len(subcontract) > 0:
                subcontractcopy = subcontract.copy()
                for sub_contract in subcontractcopy:
                    if re.search('议案|公告|公示|合同法|备忘录',sub_contract):
                        subcontract.remove(sub_contract)
                        continue
                    if re.search('合同|协议|[a-zA-Z]', sub_contract) is None:
                        subcontract.remove(sub_contract)                    
                if len(subcontract) > 0:
                    count = dict()
                    for i in subcontract:
                        if i in count:
                            count[i] = count[i] + 1
                        else:
                            count[i] = 1
                    contract.append(refine_contract(max(count)))
                else:
                    contract.append('')
            else:
                contract.append('')
        return(contract)
    return ('')
                
                    
                    
        
    
    
def execute():
    file = open('D:/Tianchi/data/round1_train_20180518/重大合同/hetong.train', 'r', encoding = 'utf-8-sig')
    hetong_train = csv.reader(file, delimiter = '\t')
    hetong_train = list(hetong_train)
    file.close()
    hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df = pd.DataFrame(columns = ['公告id', '合同名称'])
    i = 0
    lst = []
    #lst_int = []
    for i in os.listdir(path):
        #lst_int.append(int(i.replace('.html', '')))
        lst.append(i)
    #df['公告id'] = lst_int
    ggid = []
    contract_all = []
    for filename in lst:
        print(filename)
        htmlf = open(path + filename, 'r', encoding = 'utf-8')
        htmlcont = htmlf.read()
        htmlf.close()
        soup = BeautifulSoup(htmlcont,'lxml')
        
        ##################################################
        contract = match_contract(soup)
        if type(contract) is str:
            ggid.append(int(filename.replace('.html', '')))
            contract_all.append(contract)
            print(contract)
            # time.sleep(0.1)
        else:
            if len(contract) == 0:
                ggid.append(int(filename.replace('.html', '')))
                contract_all.append('')
            else:
                for i in range(len(contract)):
                    ggid.append(int(filename.replace('.html', '')))
                    contract_all.append(contract[i])
                    print(contract[i])
                    #time.sleep(0.1)
        ################################################
    df['公告id'] = ggid
    df['合同名称'] = contract_all 
    writer = pd.ExcelWriter('Save_contract.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()
    

if __name__ == '__main__':
    execute()