# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 11:05:58 2018

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

#pat_partyb1 = '(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司|局|业|院|委|室|部|中心|银行|电视台)'
#re.sub('<.+>|\n|\s', '', str(soup))
#soupcontent.replace('本公司', 'bengongsi')


def part_join(word, part):
    # Join the word according to the part
    part.reverse()
    word.reverse()
    if len(word) <= 2:
        return word
    else:
        for i in range(2,len(word)):
            if 'n' not in part[i]:
                if len(part) > (i+1) and re.search('n', part[i+1]):
                    continue
                else:
                    break
    new_word = word[0:i]
    new_word.reverse()
    word = ''.join(new_word)
    return word
        



def match_partya(soup, partya_diclist, end):
    partya = ''
    soupcontent = re.sub('<.+>|\n|   ', '', str(soup))
    soupcontent = soupcontent.replace('本公司', 'bengongsi')
    soupcontent = soupcontent.replace('子公司', 'zigongsi')
    la_raw = re.findall('(\w+|\w+(（\w*）|\(\w*\))\w*)(公司|' + end +')', soupcontent)
    la_raw = [''.join(x) for x in la_raw]
    # 1 Searh the dictionary of party_a from train data
    dic_tag = 0
    
    # 2 甲方等
    if re.search('(收到|接到)(了|了由|由)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司)', soupcontent):
        raw = re.search('(收到|接到)(了|了由|由)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司)', soupcontent)
        partya = raw.group(3) + raw.group(5)
        partya = re.sub('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方','',partya)
        if re.search('招标', partya) is None:
            return partya
    elif re.search('(收到|接到)(了|了由|由)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)' + '(' + end + ')', soupcontent):
        raw = re.search('(收到|接到)(了|了由|由)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)' + '(' + end + ')', soupcontent)
        partya = raw.group(3) + raw.group(5)
        partya = re.sub('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方','',partya)
        if re.search('招标', partya) is None:
            return partya
    
    
    if re.search('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方', soupcontent):
        if re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方)(：|是|为)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司)', soupcontent):
            raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方)(：|是|为)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)(公司)', soupcontent)
            partya = raw.group(3) +raw.group(5)
        elif re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方)(：|是|为)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)' + '(' + end + ')', soupcontent):
            raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方)(：|是|为)?(\w+?|\w+?(（\w*）|\(\w*\))\w*?)' + '(' + end + ')', soupcontent)
            partya = raw.group(3) +raw.group(5)
        else:
            ob_loc = next(re.finditer('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方', soupcontent)).start()
            ob = soupcontent[max(0, ob_loc-20) : min(len(soupcontent)-1, ob_loc+20)]
            if re.search('(\w+|\w+(（\w*）|\(\w*\))\w*)(公司)', ob):
                partya_raw = re.search('(\w+|\w+(（\w*）|\(\w*\))\w*)(公司)', ob).group()
                seg = jieba.posseg.cut(partya_raw)
                word = []
                part = []
                for i in seg:
                    word.append(i.word)
                    part.append(i.flag)
                partya = part_join(word.copy(), part.copy())

            elif re.search('(\w+|\w+(（\w*）|\(\w*\))\w*)' + '(' + end + ')', ob):
                partya_raw = re.search('(\w+|\w+(（\w*）|\(\w*\))\w*)' + '(' + end + ')', ob).group()
                seg = jieba.posseg.cut(partya_raw)
                word = []
                part = []
                for i in seg:
                    word.append(i.word)
                    part.append(i.flag)
                partya = part_join(word.copy(), part.copy())
    return partya
    
        
def execute():
    file = open('D:/Tianchi/data/round1_train_20180518/重大合同/hetong.train', 'r', encoding = 'utf-8-sig')
    hetong_train = csv.reader(file, delimiter = '\t')
    hetong_train = list(hetong_train)
    file.close()
    hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])
    # Get the dictionary of the party A 
    partya_diclist = list(set(hetong_train['甲方']))
    partya_diclist.pop(0)
    partya_diclist = partya_diclist[0:500]
    # Get the dictionary of the end of the party A
    # Remove company
    end_raw = [jieba.lcut(x).pop() for x in hetong_train['甲方'] if x]
    end_raw = list(set(end_raw))
    end_raw.remove('公司')
    end_raw = [x for x in end_raw if len(x) > 2 and len(x) < 5]
    end = '|'.join(end_raw)
    path = 'D:/Tianchi/data/round1_train_20180518/重大合同/html/'
    df = pd.DataFrame(columns = ['公告id', '甲方'])
    i = 0
    lst = []
    #lst_int = []
    for i in os.listdir(path):
        #lst_int.append(int(i.replace('.html', '')))
        lst.append(i)
    #df['公告id'] = lst_int
    ggid = []
    partya_all = []
    for filename in lst:
        htmlf = open(path + filename, 'r', encoding = 'utf-8')
        htmlcont = htmlf.read()
        htmlf.close()
        soup = BeautifulSoup(htmlcont,'lxml')
        
        ##################################################
        partya = match_partya(soup, partya_diclist, end)
        #df.loc[df['公告id'] == int(filename.replace('.html', '')), '乙方'] = partyb
        if type(partya) is str:
            ggid.append(int(filename.replace('.html', '')))
            partya_all.append(partya)
            print(filename)
            print(partya)
            # time.sleep(0.1)
        else:
            if len(partya) == 0:
                ggid.append(int(filename.replace('.html', '')))
                partya_all.append('')
            else:
                for i in range(len(partya)):
                    ggid.append(int(filename.replace('.html', '')))
                    partya_all.append(partya[i])
                    print(filename)
                    print(partya[i])
                    #time.sleep(0.1)
        ################################################
    df['公告id'] = ggid
    df['甲方'] = partya_all
    writer = pd.ExcelWriter('Save_partya.xlsx')
    df.to_excel(writer, 'page_1', float_format = '%.5f', index = False,
                header = False, encoding = 'utf-8')
    writer.save()
    

if __name__ == '__main__':
    execute()
