# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 09:47:14 2018

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
import fool
from Function_temp import *

def find_full_name(soup):
    # 找出公告发出公司
    soupcontent = re.sub('\n|\s', '', soup.get_text())
    _, nt = fool.analysis(soupcontent[0:110])
    nt = nt[0]
    fullname_ls = [x[3] for x in nt if x[2] == 'company' or x[2] == 'org']
    fullname_ls_len = [len(x) for x in fullname_ls[:min(2, len(fullname_ls))]]
    if len(fullname_ls_len):
        fullname = fullname_ls[:max(2, len(fullname_ls))][fullname_ls_len.index(max(fullname_ls_len))]
        if fullname:
            return(fullname)
        else:
            return('公告里没有公司')
    return('公告里没有公司')
            
def refine_company_list(company_list, simply_ls):
    # simply_ls 主要为公司简称
    # company_list 为NER识别出的公司或组织
    # 去掉company_list 中带有simply_ls 的元素
    for simply in simply_ls:
        if simply in company_list:
            index = company_list.index(simply)
            company_list.pop(index)
    return(company_list)


def find_partya(soupcontent, div):
    # 找甲方
    for i in div[1:]:
        if i.get('title'):
            if re.search('采购人|采购方|业主方|招标方|招标人|招标单位|发包方|发包人|甲方|买方', i.get('title')):
                if re.search('：', i.get('title')):
                    loc = i.get('title').index('：')
                    if len(i.get('title')[(loc+1):]) > 1:
                        raw = i.get('title')[(loc+1):]
                        _, nt = fool.analysis(raw)
                        nt = nt[0]
                        raw_ls = [x[3] for x in nt if x[2] == 'company' or x[2] == 'org']
                        if len(raw_ls):
                            raw_ls_len = [len(x) for x in raw_ls]
                            raw = raw_ls[raw_ls_len.index(max(raw_ls_len))]
                            if raw:
                                return (raw)
                divcontent = i.get_text()
                divcontent = re.sub('\n | ', '', divcontent)
                divcontent_split = re.split('\n', divcontent)
                divcontent_split = [x for x in divcontent_split if len(x) > 0]
                if len(divcontent_split) == 1 and re.search('，|、', divcontent_split[0]) is None:
                    raw = divcontent_split[0]
                    _, nt = fool.analysis(raw)
                    nt = nt[0]
                    raw_ls = [x[3] for x in nt if x[2] == 'company' or x[2] == 'org']
                    raw_ls_len = [len(x) for x in raw_ls]
                    if len(raw_ls_len):
                        raw = raw_ls[raw_ls_len.index(max(raw_ls_len))]
                        if raw:
                            return (raw)
    soupcontent = re.sub('\n|\s', '', soupcontent.capitalize())
    _, nt = fool.analysis(soupcontent)
    nt = nt[0]
    raw_ls = [x[3] for x in nt if (x[2] == 'company' or x[2] == 'org') and len(x[3]) >= 3 and x[0]>25 and re.search('招标|中标|投标|政府投资', x[3]) is None]
    if len(raw_ls):
        # 得到实体的一个list
        simply_ls = re.findall('“(\w+?)”', soupcontent)
        company_ls = refine_company_list(list(set(raw_ls)).copy(), simply_ls)
        company_ls.sort(key = lambda x: len(x), reverse = True)
        # 得到实体的结尾词
        company_end = [x[(len(x)-2):] for x in company_ls]
        company_end = list(set(company_end))
        company_end = '(' + '|'.join(list(set(company_end))) + ')'
        # 正则1
        reg_one = re.search('([\w\(\)（）—~\-\.]+)' + company_end + '(\(|（)(以)?下(简)?称(：|“|”|，|、|\w)*?“?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位|采购人|采购方)', soupcontent)
        if reg_one:
            reg_one = reg_one.group()
            if re.search('与|和|及', reg_one):
                reg_one = re.search('(与|和|及).+', reg_one).group()
            for comp in company_ls:
                comp = re.sub('\(', '\(', comp); comp = re.sub('\)', '\)', comp); comp = re.sub('\-', '\-', comp); comp = re.sub('\.', '\.', comp); comp = re.sub('\*', '\*', comp)
                if re.search(comp, reg_one):
                    return(re.sub('\\\\', '',comp))
        # 构建实体的一个dict并初始化
        #company_dic = dict()
        #for comp in company_ls:
        #    company_dic[comp] = 0
        # 正则2
        reg_two = re.findall('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位|采购人|采购方|项目实施机构|公司名称)(：|是|为)*([\w\(\)（）—~\-\.]*)'+ company_end, soupcontent)
        if reg_two:
            reg_two = [''.join(x) for x in reg_two]
            for comp in company_ls:
                comp = re.sub('\(', '\(', comp); comp = re.sub('\)', '\)', comp); comp = re.sub('\-', '\-', comp); comp = re.sub('\.', '\.', comp); comp = re.sub('\*', '\*', comp)
                for reg in reg_two:
                    if re.search(comp, reg):
                        return(re.sub('\\\\', '',comp))
            if len(reg_two) == 1:
                reg = re.search('(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位|采购人|采购方|项目实施机构|公司名称)(：|是|为)*([\w\(\)（）—~\-\.]*)'+ company_end, reg_two[0])
                if re.search('金额|项目|工程',reg.group(3)) is None:
                    return(reg.group(3) + reg.group(4))
        # 正则3
        reg_three = re.findall('(收到|接到|获|获得|根据|依据|为)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位|采购人|采购方)?([\w\(\)（）—~\-\.]*)' + company_end + '([\w\(\)（）—~\-\.“”《》、]*)(中标)', soupcontent)
        if reg_three:
            reg_three = [''.join(x) for x in reg_three if re.search('招标代理|招标机构|招标公司', ''.join(x)) is None]
            for comp in company_ls:
                comp = re.sub('\(', '\(', comp); comp = re.sub('\)', '\)', comp); comp = re.sub('\-', '\-', comp); comp = re.sub('\.', '\.', comp); comp = re.sub('\*', '\*', comp)
                for reg in reg_three:
                    if re.search(comp, reg):
                        return(re.sub('\\\\', '',comp))
            if len(reg_three) == 1:
                reg = re.search('(收到|接到|获|获得|根据|依据|为)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位|采购人|采购方)?([\w\(\)（）—~\-\.]*)' + company_end + '([\w\(\)（）—~\-\.“”《》、]*)(中标)', reg_three[0])
                if re.search('金额|项目|工程',reg.group(5)) is None:
                    return(reg.group(5) + reg.group(6))
        # 正则4
        reg_four = re.findall('(收到|和|与|、)([\w\(\)（）—~\-\.]*?)' + company_end + '([\w\(\)（）—~\-\.“”：]*?)(签订|签署|签定)', soupcontent)
        if reg_four:
            reg_four = [''.join(x) for x in reg_four if re.search('招标代理|招标机构', ''.join(x)) is None]
            for comp in company_ls:
                comp = re.sub('\(', '\(', comp); comp = re.sub('\)', '\)', comp); comp = re.sub('\-', '\-', comp); comp = re.sub('\.', '\.', comp); comp = re.sub('\*', '\*', comp)
                for reg in reg_four:
                    if re.search(comp, reg):
                        return(re.sub('\\\\', '',comp))
            if len(reg_four) == 1:
                reg = re.search('(收到|和|与|、)([\w\(\)（）—~\-\.]*?)' + company_end + '([\w\(\)（）—~\-\.“”：]*?)(签订|签署|签定)', reg_four[0])
                if re.search('金额|项目|工程',reg.group(2)) is None:
                    return(reg.group(2) + reg.group(3))
        # 正则5
        reg_five = re.findall('为([\w\(\)（）—~\-\.]*?)' + company_end +'([\w\(\)（）—~\-\.“”：《》]*?)(中标候选人|中标单位)', soupcontent)
        if reg_five:
            reg_five = [''.join(x) for x in reg_five]
            for comp in company_ls:
                comp = re.sub('\(', '\(', comp); comp = re.sub('\)', '\)', comp); comp = re.sub('\-', '\-', comp); comp = re.sub('\.', '\.', comp); comp = re.sub('\*', '\*', comp)
                for reg in reg_five:
                    if re.search(comp, reg):
                        return(re.sub('\\\\', '',comp))
            if len(reg_five) == 1:
                reg = re.search('([\w\(\)（）—~\-\.]*?)' + company_end +'([\w\(\)（）—~\-\.“”：《》]*?)(中标候选人|中标单位)', reg_five[0])
                if re.search('金额|项目|工程',reg.group(1)) is None:
                    return(reg.group(1) + reg.group(2))
        # 正则6
        reg_six = re.findall('(“[\w\(\)（）—~\-\.、]+?”)|(《[\w\(\)（）—~\-\.、]+?》)', soupcontent)
        if reg_six:
            reg_six = [''.join(x) for x in reg_six if len(''.join(x)) > 10]
            for comp in company_ls:
                comp = re.sub('\(', '\(', comp); comp = re.sub('\)', '\)', comp); comp = re.sub('\-', '\-', comp); comp = re.sub('\.', '\.', comp); comp = re.sub('\*', '\*', comp)
                for reg in reg_six:
                    if re.search(comp, reg):
                        return(re.sub('\\\\', '',comp))
        # 正则7
        reg_seven = re.findall('(收到|接到|获|获得|中标|参与|参加)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位|采购人|采购方)?([\w\(\)（）—~\-\.]*)' + company_end, soupcontent[100:])
        if reg_seven:
            reg_seven = [''.join(x) for x in reg_seven if re.search('招标代理|招标机构', ''.join(x)) is None]
            for comp in company_ls:
                comp = re.sub('\(', '\(', comp); comp = re.sub('\)', '\)', comp); comp = re.sub('\-', '\-', comp); comp = re.sub('\.', '\.', comp); comp = re.sub('\*', '\*', comp)
                for reg in reg_seven:
                    if re.search(comp, reg):
                        return(re.sub('\\\\', '',comp))
            if len(reg_seven) == 1:
                reg = re.search('(收到|接到|获|获得|中标|参与|参加)(了)?(由)?(甲方|买方|销售方|业主方|业主|招标人|招标单位|招标方|发包人|发包方|分包人|采购单位|采购人|采购方)?([\w\(\)（）—~\-\.]*)' + company_end, reg_seven[0])
                if re.search('金额|项目|工程',reg.group(5)) is None:
                    return(reg.group(5) + reg.group(6))
        return('')
    else:
        return('')
def find_partyb(full_name, content):
    # 找乙方
    lb = []
    reg_one = re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content)
    reg_two = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为|\)|）)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司|局|院|馆|委员会|集团|室|部|中心)', content)
    if reg_one or reg_two:
        if reg_one:
            if re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content):
                partyb_raw = re.search('([\w|\(|\)|（|）|\-|\.]+?)(公司)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content)
            else:
                partyb_raw = re.search('([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心)((\(|（)(以)?下(简)?称(“|”|，|、|\w)*?“?(乙方|承包人|承包方|卖方|中标人))', content)
            if full_name in partyb_raw.group() or len(partyb_raw.group(1) + partyb_raw.group(2)) < 6:
                lb.append(full_name)
            else:
                result = re.sub('\w+子公司', '', partyb_raw.group(1) + partyb_raw.group(2))
                lb.append(result)
        elif reg_two and re.search('和|与|合同|合资',reg_two.group()) is None:
            if  re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为|\)|）)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content):
                partyb_raw = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为|\)|）)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(公司)', content)
            else:
                partyb_raw = re.search('(乙方|承包人|承包方|卖方|中标人)(：|是|为|\)|）)?(\n)?([\w|\(|\)|（|）|\-|\.]+?)(局|院|馆|委员会|集团|室|部|中心)', content)
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
            lb_refine = [x[1] + x[3] for x in lb_raw if re.search('(与|和|或|中标)', ''.join(x)) is None]
            if len(lb_refine):
                _ = [lb.append(x) for x in list(set(lb_refine)) if re.search('子公司', x) is None]
            elif len(re.findall('(子公司|全资公司)(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|馆|委员会|集团|室|部|中心)', content)):
                lb_raw = re.findall('(子公司|全资公司)(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|馆|委员会|集团|室|部|中心)', content)
                lb_refine = [x[1] + x[3] for x in lb_raw if re.search('(与|和|或|中标)', ''.join(x)) is None]
                _ = [lb.append(x) for x in list(set(lb_refine)) if re.search('子公司', x) is None]
        elif len(re.findall('(子公司|全资公司)(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|馆|委员会|集团|室|部|中心)', content)):
            lb_raw = re.findall('(子公司|全资公司)(\w+|\w+(（\w*）|\(\w*\))\w*)(局|院|馆|委员会|集团|室|部|中心)', content)
            lb_refine = [x[1] + x[3] for x in lb_raw if re.search('(与|和|或|中标)', ''.join(x)) is None]
            _ = [lb.append(x) for x in list(set(lb_refine)) if re.search('子公司', x) is None]
    return (lb)
    
      
def tiejian_key(soup):
    # 只匹配中国铁建
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    content_split = re.split('一、本|二、本|三、本|四、本|五、本|六、本|七、本|八、本|九、本|十、本|\d、本|\d.本公司', soupcontent)
    if len(content_split) > 1:
        content_split.pop(0)
    pat_partya = '公司收到(.+?)(发出的)?中标通知书'
    pat_partyb = '(所属子公司|下属子公司|所属|下属|子公司|、|及|和)([\w|（|）|\(|\)]+?)(公司)'
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
        ob_partya = refine_partya(ob_partya)
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
        ob_partya = refine_partya(ob_partya)
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
    # Company 没有用
    full_name = find_full_name(soup)
    # 对于中国铁建和中国北车的公告
    if full_name[0:4] == '中国铁建':
        key = tiejian_key(soup)
        if type(key) is zip:
            return(key)
    if full_name[0:4] == '中国北车' or full_name[0:4] == '中国中车' or full_name[0:4] == '中国南车':
        key = beiche_key(soup, full_name)
        if type(key) is zip:
            return(key)
    soupcontent = re.sub('\n | ', '', soup.get_text())
    partya = []
    partyb = []
    combo = []
    # 先找乙方关键词
    # 甲方结尾可为(公司|局|院|馆|委员会|集团|室|部|中心|银行|[A-Za-z|\-]+)
    soupcontent = re.sub('本公司|我公司|占公司|对公司|是公司|影响公司|为公司|项目公司|后公司|提升公司|上述公司|及公司|与公司', '', soupcontent)
    lb = find_partyb(full_name, soupcontent)
    soupcontent = re.sub('控股子公司|子公司', '', soupcontent)
    #if len(lb) <= 1:
        # 如果只有一个或者没有子公司，即一个乙方
    if len(lb) == 0:
        partyb.append(full_name)
    else:
        if re.search('与|和', lb[0]):
            partyb.append(lb[0][(re.search('与|和', lb[0]).start()+1):])
        else:
            partyb.append(lb[0])
    if re.search('联合体|联合中标|分别收到|丙方|共同', soupcontent):
        # 如果联合体存在
        content_split = re.split('\n|，|。', soupcontent)
        content_split = [x for x in content_split if len(x) > 0]
        for content in content_split:
            if re.search('联合体成员：', content):
                combo_raw = re.search('联合体成员：([\w、]+)', content)
                combo.append(combo_raw.group(1))
                break
            if re.search('联合体|联合中标|分别收到|丙方|共同', content):
                loc = content.index(re.search('联合体|联合中标|分别收到|丙方|共同', content).group())
                combo_raw = re.findall('(与|和|、)“?([\w|\(|\)|（|）|\-|\.]+)(公司|局|院|馆|委员会|室|部|中心|银行)', content[:loc])
                combo_raw = [x[1] + x[2] for x in combo_raw]
                combo_raw = [x for x in combo_raw if len(x) > 5 and x != partyb[0]]
                combo.append('、'.join(combo_raw))
                break
    if len(combo) == 0:
        combo.append('')
    pat_temp = partyb[0] + '|' + re.sub('、', '|', combo[0])
    pat_temp = re.sub('\(', '\(', pat_temp); pat_temp = re.sub('\)', '\)', pat_temp)
    soupcontent = re.sub(pat_temp, '', soupcontent)
    div = soup.findAll('div')
    #寻找甲方
    result_a = find_partya(soupcontent, div)
    if result_a is not None:
        partya.append(result_a)
    else:
        partya.append('')
    return(zip(refine_partya(partya), partyb, combo))