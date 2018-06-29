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

# suibianjiayihang

def bottom_up_dp_lcs(str_a, str_b):
  """
  longest common substring of str_a and str_b
  """
  if len(str_a) == 0 or len(str_b) == 0:
    return 0
  dp = [[0 for _ in range(len(str_b) + 1)] for _ in range(len(str_a) + 1)]
  max_len = 0
  lcs_str = ""
  for i in range(1, len(str_a) + 1):
    for j in range(1, len(str_b) + 1):
      if str_a[i-1] == str_b[j-1]:
        dp[i][j] = dp[i-1][j-1] + 1
        max_len = max([max_len, dp[i][j]])
        if max_len == dp[i][j]:
          lcs_str = str_a[i-max_len:i]
      else:
        dp[i][j] = 0
  return (lcs_str)

def search_company(name, Company):
    for i in Company['data']:
        if i['secShortName'] == name.upper():
            return(i['secFullName'])
        if len(i) == 3:
            if name.upper() in i['secShortNameChg']:
                return(i['secFullName'])
    for i in Company['data']:
        if i['secShortName'] == name.upper()[0:4]:
            return(i['secFullName'])
        if len(i) == 3:
            if name.upper()[0:4] in i['secShortNameChg']:
                return(i['secFullName'])
    return(name)
def find_partya(content):
    reg_one = re.search('(与|和)([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)([\w|“|”|\n|（|）]*?)(签订|签署)', content)
    reg_two = re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', content)
    reg_three = re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)(（(以)?下(简)?称(“\w+”(、|或))*?“(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)”)', content)
    reg_four = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', content)
    if reg_one:
        if re.search('(与|和)([\w|\(|\)|（|）|\-|\.]+?)(公司)([\w|“|”|\n|（|）]*?)(签订|签署)', content):
            partya_raw = re.search('(与|和)([\w|\(|\)|（|）|\-|\.]+?)(公司)([\w|“|”|\n|（|）]*?)(签订|签署)', content)
        else:
            partya_raw = re.search('(与|和)([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)([\w|“|”|\n|（|）]*?)(签订|签署)', content)
        return(re.sub('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人', '', partya_raw[2] + partya_raw[3]))
    elif reg_two and re.search('招标', reg_two.group(5)) is None:
        if re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
            raw = re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
        else:
            raw = re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)', content)
        partya_raw = raw.group(5) + raw.group(6)
        return(re.sub('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人','',partya_raw))
    elif reg_three or reg_four:
        if reg_three:
            if re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(公司)(（(以)?下(简)?称(“\w+”(、|或))*?“(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)”)', content):
                partya_raw = re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(公司)(（(以)?下(简)?称(“\w+”(、|或))*?“(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)”)', content)
            else:
                partya_raw = re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)(（(以)?下(简)?称(“\w+”(、|或))*?“(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)”)', content)
            return(partya_raw.group(3) +partya_raw.group(4))
        elif reg_four:
            if re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
                partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
            else:
                partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)', content)
            return(partya_raw.group(4) +partya_raw.group(5))
        else:
            return('')

def find_partyb(full_name, content):
    lb = []
    reg_one = re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)(（(以)?下(简)?称(“\w+”(、|或))*?“(乙方|承包人|承包方|卖方|中标人)”)', content)
    reg_two = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', content)
    if reg_one or reg_two:
        if reg_one:
            if re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司)(（(以)?下(简)?称(“\w+”(、|或))*?“(乙方|承包人|承包方|卖方|中标人)”)', content):
                partyb_raw = re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司)(（(以)?下(简)?称(“\w+”(、|或))*?“(乙方|承包人|承包方|卖方|中标人)”)', content)
            else:
                partyb_raw = re.search('([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)(（(以)?下(简)?称(“\w+”(、|或))*?“(乙方|承包人|承包方|卖方|中标人)”)', content)
            if full_name in partyb_raw.group() or len(partyb_raw.group(1) + partyb_raw.group(2)) < 7:
                lb.append(full_name)
            else:
                lb.append(partyb_raw.group(1) + partyb_raw.group(2))
        elif reg_two and re.search('和|与',reg_two.group()) is None:
            if  re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
                partyb_raw = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
            else:
                partyb_raw = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)', content)
            if full_name in partyb_raw.group() or len(partyb_raw.group(4) + partyb_raw.group(5)) < 7:
                lb.append(full_name)
            else:
                lb.append(partyb_raw.group(4) + partyb_raw.group(5))
        else:
            lb.append(full_name)
    # 找出合同中的子公司
    elif re.search('子公司|全资公司', content):
        if len(re.findall('(子公司|全资公司)(\w*?|\w*?(（\w*）|\(\w*\))\w*?)(公司)', content)):
            lb_raw = re.findall('(子公司|全资公司)(\w*?|\w*?(（\w*）|\(\w*\))\w*?)(公司)', content)
            lb_refine = [x[1] + x[3] for x in lb_raw if re.search('(和|或)', ''.join(x)) is None]
            _ = [lb.append(x) for x in list(set(lb_refine))]
        elif len(re.findall('(子公司|全资公司)(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|馆|委员会|集团|室|部|中心|银行)', content)):
            lb_raw = re.findall('(子公司|全资公司)(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|馆|委员会|集团|室|部|中心|银行)', content)
            lb_refine = [x[1] + x[3] for x in lb_raw if re.search('(和|或)', ''.join(x)) is None]
            _ = [lb.append(x) for x in list(set(lb_refine))]
    return (lb)

    

def refine_partya_key(partya):
    for i in range(len(partya)):
        if re.search('是', partya[i]):
            j = partya[i]
            partya[i] = partya[i][(j.index('是')+1):]
    partya = [re.sub('\-', '', x) for x in partya]
    partya = [re.sub('（', '(', x) for x in partya]
    partya = [re.sub('）', ')', x) for x in partya]
    return (partya)
def refine_partyb_key(partyb):
    # 去掉乙方及联合体中的括号
    partyb = [re.sub('（', '(', x) for x in partyb]
    partyb = [re.sub('）', ')', x) for x in partyb]
    partyb = [re.sub('\(.*\)', '', x) for x in partyb]
    return (partyb)

      
def tiejian_key(soup):
    # 只匹配中国铁建
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    content_split = re.split('一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|\d、', soupcontent)
    if type(content_split) is list:
        content_split.pop(0)
    pat_partya = '公司收到(.+?)(发出的)?中标通知书'
    pat_partyb = '(子公司|、|及|和)([\w|（|）|\(|\)]+?)(公司)'
    ob_partya = []
    ob_partyb = []
    ob_combo = []
    for content in content_split:
        if re.search(pat_partya, content):
            ob_partya.append(re.search(pat_partya, content).group(1))
        else:
            ob_partya.append('')    
        ob_b = re.findall(pat_partyb, content)
        ob_b = [x[1] + x[2] for x in ob_b]
        ob_b = [x for x in ob_b if len(x) > 6]
        if len(ob_b) == 0:
            continue
        ob_partyb.append(ob_b[0])
        ob_combo.append('、'.join(ob_b[1:]))
    if len(ob_partyb) == 0:
        return('') 
    else:
        ob_partya = refine_partya_key(ob_partya)
        ob_partyb = refine_partyb_key(ob_partyb)
        ob_combo = refine_partyb_key(ob_combo)
        return(zip(ob_partya, ob_partyb, ob_combo))
        
def beiche_key(soup):
    # 只匹配中国北车
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    content_split = re.split('\d、', soupcontent)
    if type(content_split) is list:
        content_split.pop(0)
    pat_partya = '与(.+?)签订了'
    pat_partyb = '(子公司|、|及|和)([\w|（|）|\(|\)]+?)(公司)'
    ob_partya = []
    ob_partyb = []
    ob_combo = []
    for content in content_split:
        if re.search(pat_partya, content):
            ob_partya.append(re.search(pat_partya, content).group(1))
        else:
            ob_partya.append('')
        ob_b = re.findall(pat_partyb, content)
        ob_b = [x[1] + x[2] for x in ob_b]
        ob_b = [x for x in ob_b if len(x) > 6]
        if len(ob_b) == 0:
            continue
        ob_partyb.append(ob_b[0])
        ob_combo.append('、'.join(ob_b[1:]))
        # 乙对多个甲
        if re.search('分别', ob_partya[len(ob_partya)-1]):
            partya = ob_partya.pop()
            partya = re.sub('分别', '', partya)
            partya = re.split('、|和|以及|及|', partya)
            _ = [ob_partya.append(x) for x in partya]
            ob_partyb.append(ob_b[0])
            ob_combo.pop()
            ob_combo.append('')
            ob_combo.append('')
    if len(ob_partyb) == 0:
        return('')
    else:
        ob_partya = refine_partya_key(ob_partya)
        ob_partyb = refine_partyb_key(ob_partyb)
        ob_combo = refine_partyb_key(ob_combo)
        return(zip(ob_partya, ob_partyb, ob_combo))
        
def part_join(word, part):
    # Join the word according to the part
    part.reverse()
    word.reverse()
    if len(word) <= 2:
        return (''.join(word))
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


def match_key(soup, Company):
    div = soup.findAll('div')
    div_0 = div[0]
    title = re.sub('\*', '\*', div_0.get('title'))
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    ## 找出公司全称
    if re.search('([\d|\s]+)?([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:100])):
        name = re.search('([\d|\s]+)?([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:100])).group(2)
        if name[0] == '一' or name[0] == '号':
            # 因格式问题造成的在开头或结尾可能多出一个一
            full_name = name[1:]
        elif name[len(name)-1] == '一':
            full_name = name[1:(len(name)-1)]
        else:
            full_name = name
    elif re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:100]):
        name = re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:100]).group(3)
        full_name = search_company(name, Company)
    else:
        full_name = search_company(div_0.get('title')[0:4], Company)
    # 对于中国铁建和中国北车的公告
    if full_name[0:4] == '中国铁建':
        key = tiejian_key(soup)
        if type(key) is zip:
            return(key)
    if full_name[0:4] == '中国北车':
        key = beiche_key(soup)
        if type(key) is zip:
            return(key)
    soupcontent = re.sub('<.+>|\n | ', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    partya = []
    partyb = []
    combo = []
    # 先找乙方关键词
    # 甲方结尾可为(公司|局|院|馆|委员会|集团|室|部|中心|银行|[A-Za-z|\-]+)
    soupcontent = re.sub('本公司|我公司|占公司|对公司|影响公司|为公司|项目公司|后公司', '', soupcontent)
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
                    combo_raw = [x for x in combo_raw if len(x) > 6]
                    combo.append('、'.join(combo_raw))
                    break
            # 找到联合体后在相同的段落里找甲方
            if combo[0] == '':
                # 如果没有匹配到联合体，则从全文中找甲方
                content_split = [soupcontent]
            else:
                content_split = re.split('\n', soupcontent)
                content_split = [x for x in content_split if len(x) > 0]
                # 对content加一些转义字符
            content = re.sub('\(', '\(', content)
            content = re.sub('\)', '\)', content)
            content = re.sub('\-', '\-', content)
            content = re.sub('\*', '\*', content)
            content = re.sub('\[', '\[', content)
            content = re.sub('\]', '\]', content)
            for content_ in content_split:               
                if re.search(content, content_):
                    result_a = find_partya(content_)
                    if result_a is not None:
                        partya.append(result_a)
                    else:
                        partya_raw = re.findall('([\w|\(|\)|（|）]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', content_)
                        if len(partya_raw) > 0:
                            partya_raw = [x[0] + x[1] for x in partya_raw]
                            partya_raw = [x for x in partya_raw if x not in partyb[0] and x not in combo[0] and x not in full_name]
                            if len(partya_raw) == 0:
                                partya.append('')
                            else:
                                partya.append(partya_raw[0])
                        else:
                            partya.append('')
                    return(zip(refine_partya_key(partya), refine_partyb_key(partyb), refine_partyb_key(combo)))
            partya.append('')
            return(zip(refine_partya_key(partya), refine_partyb_key(partyb), refine_partyb_key(combo)))
        else:
            combo.append('')
            pat_temp = partyb[0] + '|' + full_name
            pat_temp = re.sub('\(', '\(', pat_temp)
            pat_temp = re.sub('\)', '\)', pat_temp)
            soupcontent = re.sub(pat_temp, '', soupcontent)
            #不存在联合体，直接寻找甲方
            result_a = find_partya(soupcontent)
            if result_a is not None:
                partya.append(result_a)
            else:
                content_split = re.split('\n|,', soupcontent)
                #content_split = [re.sub(pat_temp, '', x) for x in content_split if len(x) > 0]
                content_split = [x for x in content_split if len(x) > 0]
                content_split = [x for x in content_split if re.search('([\w|\(|\)|（|）]+)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', x)]
                company_split = [re.search('([\w|\(|\)|（|）]+)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', x).group() for x in content_split]
                if len(company_split) == 1 and len(company_split[0]) < 7:
                    partya.append('')
                elif len(company_split) == 1:
                    partya_raw = company_split[0]
                    seg = jieba.posseg.cut(partya_raw)
                    word = []
                    part = []
                    for i in seg:
                        word.append(i.word)
                        part.append(i.flag)
                    partya.append(part_join(word.copy(), part.copy()))
                else:
                    dic_company = dict()
                    for i in range(len(company_split)):
                        for j in range(i,len(company_split)):
                            sub_result = bottom_up_dp_lcs(company_split[i], company_split[j])
                            if re.search('公司|局|院|馆|委员会|集团|室|部|中心|银行', sub_result):
                                if sub_result in dic_company:
                                    dic_company[sub_result] = dic_company[sub_result] + 1
                                else:
                                    dic_company[sub_result] = 1
                    if len(dic_company) == 0 or len(max(dic_company)) < 7:
                        partya.append('')
                    else:
                        partya.append(max(dic_company))                                
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