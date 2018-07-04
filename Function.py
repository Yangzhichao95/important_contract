# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 10:22:20 2018

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

def find_full_name(soup, Company):
    div = soup.findAll('div')
    div_0 = div[0]
    title = re.sub('\*', '\*', div_0.get('title'))
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    ## 找出公司全称
    if re.search('(\d+)?([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])):
        if re.search('号([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])):
            name = re.search('号([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])).group(1)
        else:
            name = re.search('(\d+)?([\w|（|）|\(|\)]+)' + re.sub('（一）|（二）|（三）|（四）|（五）|“|”', '', title), re.sub('“|”', '', soupcontent[0:120])).group(2)
        if name[0] == '一' or name[0] == '号':
            # 因格式问题造成的在开头或结尾可能多出一个一
            full_name = name[1:]
        elif name[len(name)-1] == '一':
            full_name = name[1:(len(name)-1)]
        else:
            full_name = name
    elif re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:120]):
        name = re.search('(简称|名称)(:|：)?([\w|*]+?)(公告|编号|编码|\(|\)|股票代码|证券代码)', soupcontent[0:120]).group(3)
        full_name = search_company(name, Company)
    else:
        full_name = search_company(div_0.get('title')[0:4], Company)
    return (full_name)
    

def find_partya(content, div):
    # 首先对于小标题只在html title里的情况
    for i in div[1:]:
        if i.get('title'):
            if re.search('采购人|采购方：|业主方|招标方|招标人|招标单位|发包方|发包人|甲方|买方', i.get('title')):
                if re.search('：', i.get('title')):
                    loc = i.get('title').index('：')
                    if i.get('title')[(loc+1):] != '':
                        return (i.get('title')[(loc+1):])
                divcontent = i.get_text()
                divcontent = re.sub('\n | ', '', divcontent)
                divcontent_split = re.split('\n', divcontent)
                divcontent_split = [x for x in divcontent_split if len(x) > 0]
                if len(divcontent_split) == 1 and re.search('，|。|、', divcontent_split[0]) is None:
                    return (divcontent_split[0])
    #
    reg_one = re.search('(和|与)([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)([\w|“|”|\n|（|）]*?)(签订|签署)', content)
    reg_two = re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行|处|人民政府)', content)
    reg_three = re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位))', content)
    reg_four = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)', content)
    if reg_one:
        if re.search('(与|和)([\w|\(|\)|（|）|\-|\.]+?)(公司)([\w|“|”|\n|（|）]*?)(签订|签署)', content):
            partya_raw = re.search('(与|和)([\w|\(|\)|（|）|\-|\.]+?)(公司)([\w|“|”|\n|（|）]*?)(签订|签署)', content)
        else:
            partya_raw = re.search('(与|和)([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)([\w|“|”|\n|（|）]*?)(签订|签署)', content)
        return(re.sub('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位', '', partya_raw[2] + partya_raw[3]))
    elif reg_two and re.search('招标', reg_two.group(5)) is None:
        if reg_four and re.search('招标', reg_four.group(4)) is None:
            if re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
                partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
                if re.search('招标', partya_raw.group(4)):
                    partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)', content)
            else:
                partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)', content)
            return(partya_raw.group(4) +partya_raw.group(5))
        if re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
            raw = re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
            if re.search('招标', raw.group(5)):
                # 246185的特殊情况
                raw = re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|处|人民政府)', content)
        else:
            raw = re.search('(收到|接到|获|获得|中标|参与)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|处|人民政府)', content)
        if raw:
            partya_raw = re.sub('项目为', '', raw.group(5) + raw.group(6))
            return(re.sub('甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位','',partya_raw))
        else:
            return('')
    elif reg_three or reg_four:
        if reg_three and re.search('招标', reg_three.group(3)) is None:
            if re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(公司)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位))', content):
                partya_raw = re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(公司)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位))', content)
            else:
                partya_raw = re.search('(公司|局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)?(与|和)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位))', content)
            return(partya_raw.group(3) +partya_raw.group(4))
        elif reg_four and re.search('招标', reg_four.group(4)) is None:
            if re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
                partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
                if re.search('招标', partya_raw.group(4)) or len(partya_raw.group(4)+partya_raw.group(5)) < 6:
                    partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)', content)
            else:
                partya_raw = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行|管理处|人民政府)', content)
            if partya_raw:
                return(partya_raw.group(4) +partya_raw.group(5))
            else:
                return('')
        else:
            return('')

def find_partyb(full_name, content):
    lb = []
    reg_one = re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content)
    reg_two = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心|银行)', content)
    if reg_one or reg_two:
        if reg_one:
            if re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content):
                partyb_raw = re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content)
            else:
                partyb_raw = re.search('([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content)
            if full_name in partyb_raw.group() or len(partyb_raw.group(1) + partyb_raw.group(2)) < 6:
                lb.append(full_name)
            else:
                result = re.sub('\w+子公司', '', partyb_raw.group(1) + partyb_raw.group(2))
                lb.append(result)
        elif reg_two and re.search('和|与|合同',reg_two.group()) is None:
            if  re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
                partyb_raw = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
            else:
                partyb_raw = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心|银行)', content)
            if full_name in partyb_raw.group() or len(partyb_raw.group(4) + partyb_raw.group(5)) < 6:
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
    # refine the output
    for i in range(len(partya)):
        if re.search('是', partya[i]):
            j = partya[i]
            partya[i] = partya[i][(j.index('是')+1):]
        if re.search('与', partya[i]):
            j = partya[i]
            partya[i] = partya[i][(j.index('与')+1):]
        if re.search('的', partya[i]):
            j = partya[i]
            partya[i] = partya[i][(j.index('的')+1):]
    partya = [re.sub('\-', '', x) for x in partya]
    partya = [re.sub('（', '(', x) for x in partya]
    partya = [re.sub('）', ')', x) for x in partya]
    for i in range(len(partya)):
        if len(partya[i]) < 6:
            partya[i] = ''
    return (partya)
def refine_partyb_key(partyb):
    # refine the output
    # 去掉乙方及联合体中的括号
    partyb = [re.sub('（', '(', x) for x in partyb]
    partyb = [re.sub('）', ')', x) for x in partyb]
    partyb = [re.sub('\(.*\)', '', x) for x in partyb]
    # For some case
    partyb = [re.sub('\)', '', x) for x in partyb]
    return (partyb)

      
def tiejian_key(soup):
    # 只匹配中国铁建
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    content_split = re.split('一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|\d、本|\d.本公司', soupcontent)
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
        ob_b = [x for x in ob_b if len(x) > 5]
        if len(ob_b) == 0:
            ob_partyb.append('中国铁建股份有限公司')
        else:
            ob_partyb.append(ob_b[0])
        ob_combo.append('、'.join(ob_b[1:]))
    if len(ob_partyb) == 0:
        return('') 
    else:
        ob_partya = refine_partya_key(ob_partya)
        ob_partyb = refine_partyb_key(ob_partyb)
        ob_combo = refine_partyb_key(ob_combo)
        return(zip(ob_partya, ob_partyb, ob_combo))
        
def beiche_key(soup, fullname):
    # 只匹配中国北车、中国中车、中国南车
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    content_split = re.split('\d、|\d.本公司', soupcontent)
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
        ob_b = [x for x in ob_b if len(x) > 5]
        if len(ob_b) == 0:
            ob_partyb.append(fullname)
        else:
            ob_partyb.append(ob_b[0])
        ob_combo.append('、'.join(ob_b[1:]))
        # 乙对多个甲
        if re.search('分别', ob_partya[len(ob_partya)-1]):
            partya = ob_partya.pop()
            ob_partyb.pop()
            ob_combo.pop()
            partya = re.sub('分别', '', partya)
            partya = re.split('、|和|以及|及|', partya)
            _ = [ob_partya.append(x) for x in partya]
            _ = [ob_partyb.append(ob_b[0]) for x in partya]
            _ = [ob_combo.append('') for x in partya]
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

