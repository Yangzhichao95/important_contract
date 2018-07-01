# -*- coding: utf-8 -*-
# 0.4618
"""
Created on Mon Jun 25 10:51:36 2018

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

def transfer_project(project):
    # The end of the project should not be figure
    project = re.sub(' |“|”', '', project)
    project = re.sub('（', '(', project)
    project = re.sub('）', ')', project)
    if re.search('编号', project):
        project = re.sub('(.+)', '', project)
    if len(project)>1 and  re.search('\d', project[len(project) - 1]):
        project = project[:(len(project) - 1)]
    return(project.capitalize())

def match_project(soup):
    project = ''
    partyb = match_partyb(soup)
    soupcontent = re.sub('<.+>|\n|   ', '', str(soup))
    soupcontent = re.sub('<.+>|\n|   ', '', soupcontent)
    div = soup.findAll('div')
    if type(partyb) is str or len(partyb) == 1:
        # Only one party B
        strline = ''
        for line in div[1:]:
            # 1 项目名称
            if line.get('title') and ('、项目名称：' in line.get('title') or '、工程名称：' in line.get('title') or '、中标项目：' in line.get('title') or '、采购项目名称：' in line.get('title')):
                if re.search('：([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+)', line.get('title')):
                    project = re.search('：([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+)', line.get('title')).group(1)
                    return(transfer_project(project))
                else:
                    strline = re.sub('<.+>|\n|   ', '', str(line))
                    strline = re.sub('<.+>|\n|   ', '', strline)
                    # Need refine
                    if re.search('[\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+', strline):
                        return (transfer_project(re.search('[\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+', strline).group()))
        for line in div[1:]:
            # 2 项目XX
            if line.get('title') and '项目' in line.get('title'):
                strline = re.sub('<.+>|\n|   ', '', str(line))
                strline = re.sub('<.+>|\n|   ', '', strline)
                if re.search('(项目名称|工程名称|中标内容)\w*：([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+)(，|。|；|、)', strline):
                    project = re.search('(项目名称|工程名称|中标内容)\w*：([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+)(，|。|；|、)', strline).group(2)
                    return (transfer_project(project))
        for line in div[1:]:
            # 3 “...项目”
            strline = re.sub('<.+>|\n|   ', '', str(line))
            strline = re.sub('<.+>|\n|   ', '', strline)
            if re.search('为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)的?(中标单位|中标人)', strline):
                project = re.search('为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)的?(中标单位|中标人)', strline).group(1)
                project = transfer_project(project)
                if len(project) > 5:
                    return (project)
            if re.search('在([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程)中', strline):
                content = re.search('在([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程)中', strline)
                project = content.group(1) + content.group(2)
                project = transfer_project(project)
                if len(project) > 5:
                    return (project)
            if re.search('中标项目为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|，|。)', strline):
                content = re.search('中标项目为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|，|。)', strline)
                if content.group(2) is '项目':
                    project = content.group(1) + content.group(2)
                else:
                    project = content.group(1)
                project = transfer_project(project)
                if len(project) > 5:
                    return (project)
            if re.search('(公司中标)的?([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程|，|。)', strline):
                content = re.search('(公司中标)的?([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程|，|。)', strline)
                if re.search('公告|公示', content.group()) is None:
                    if content.group(3) is'项目' or content.group(3) is '工程':
                        project = content.group(2) + content.group(3)
                    else:
                        project = content.group(2)
                    project = transfer_project(project)
                    if len(project) >5:
                        return (project)
            if re.search('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| |、]+)”', strline):
                loc = [i.start() for i in re.finditer('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| |、]+)”', strline)]
                # for try except
                content = [strline[max(0, j-15) : min(len(strline)-1, j+60)] for j in loc]
                content = [re.search('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| |、]+)(项目|采购|工程|”)', x).group() for x in content if re.search('以下简称|公示|公告|名单', x) is None and re.search('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| |、]+)(项目|采购|工程|”)', x)]
                content = [x for x in content if re.search('项目|采购|工程', x)]
                if len(content) > 0:
                    #只取第一个
                    return(transfer_project(content[0]))
                    
        # Maybe of no use
        if re.search('(项目名称|工程名称|中标内容)\w*：([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+)(，|。|；|、)', soupcontent):
            project = re.search('(项目名称|工程名称|中标内容)\w*：([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| ]+)(，|。|；|、)', soupcontent).group(2)
            project = transfer_project(project)
            if len(project) > 5:
                return (project)
        if re.search('为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)的?(中标单位|中标人)', soupcontent):
            project = re.search('为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)的?(中标单位|中标人)', soupcontent).group(1)
            project = transfer_project(project)
            if len(project) > 5:
                return (project)
        if re.search('在([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程)中', soupcontent):
            content = re.search('在([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程)中', soupcontent)
            project = content.group(1) + content.group(2)
            project = transfer_project(project)
            if len(project) > 5:
                return (project)
        if re.search('中标项目为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|，|。)', soupcontent):
            content = re.search('中标项目为([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|，|。)', soupcontent)
            if content.group(2) is '项目':
                project = content.group(1) + content.group(2)
            else:
                project = content.group(1)
            project = transfer_project(project)
            if len(project) >5:
                return (project)
        if re.search('(公司中标)的?([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程|，|。)', soupcontent):
            content = re.search('(公司中标)的?([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+?)(项目|工程|，|。)', soupcontent)
            if re.search('公告|公示' , content.group()) is None:
                if content.group(3) is'项目' or content.group(3) is '工程':
                    project = content.group(2) + content.group(3)
                else:
                    project = content.group(2)
                project = transfer_project(project)
                if len(project) > 5:
                    return(project)
        if re.search('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+)”', soupcontent):
            loc = [i.start() for i in re.finditer('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+)”', soupcontent)]
            content = [soupcontent[max(0, j-15) : min(len(soupcontent)-1, j+60)] for j in loc]
            content = [re.search('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|、| ]+)(项目|采购|工程|”)', x).group() for x in content if re.search('以下简称|公示|公告|名单', x) is None and re.search('“([\w|—|\-|~|#|·|\(|\)|（|）|\[|\]| |、]+)(项目|采购|工程|”)', x)]
            content = [x for x in content if re.search('项目|采购|工程', x)]
            if len(content) > 0:
                #只取第一个
                return(transfer_project(content[0]))
        else:
            return ('')
    return ('')
        
                
    
        



################
def execute():
    file = open('D:/Tianchi/data/round1_train_20180518/重大合同/hetong.train', 'r', encoding = 'utf-8-sig')
    hetong_train = csv.reader(file, delimiter = '\t')
    hetong_train = list(hetong_train)
    file.close()
    hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df = pd.DataFrame(columns = ['公告id', '项目名称'])
    i = 0
    lst = []
    #lst_int = []
    for i in os.listdir(path):
        #lst_int.append(int(i.replace('.html', '')))
        lst.append(i)
    #df['公告id'] = lst_int
    ggid = []
    project_all = []
    for filename in lst:
        print(filename)
        htmlf = open(path + filename, 'r', encoding = 'utf-8')
        htmlcont = htmlf.read()
        htmlf.close()
        soup = BeautifulSoup(htmlcont,'lxml')
        
        ##################################################
        project = match_project(soup)
        if type(project) is str:
            ggid.append(int(filename.replace('.html', '')))
            project_all.append(project)
            print(project)
            # time.sleep(0.1)
        else:
            if len(project) == 0:
                ggid.append(int(filename.replace('.html', '')))
                project_all.append('')
            else:
                for i in range(len(project)):
                    ggid.append(int(filename.replace('.html', '')))
                    project_all.append(project[i])
                    print(project[i])
                    #time.sleep(0.1)
        ################################################
    df['公告id'] = ggid
    df['项目名称'] = project_all 
    writer = pd.ExcelWriter('Save_project.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()
    

if __name__ == '__main__':
    execute()