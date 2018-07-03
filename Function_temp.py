# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 10:02:52 2018

@author: 25008

This is a Temp file for the function match project contract and value
"""

import re

def refine_output_contract(contract):
    # Input is a list
    contract_return = []
    for i in contract:
        contract_temp = re.sub('&lt;', '<', i)
        contract_temp = re.sub('&lt;', '<', contract_temp)
        contract_temp = re.sub('&gt;', '>', contract_temp)
        contract_temp = re.sub('（', '(', contract_temp)
        contract_temp = re.sub('）', ')', contract_temp)
        contract_temp = re.sub('《|》|/', '', contract_temp)
        contract_return.append(contract_temp.capitalize())
    return (contract_return)

def refine_output_project(project):
    # The end of the project should not be figure
    project_return = []
    for i in project:
        project_temp = re.sub('“|”|/', '', i)
        project_temp = re.sub('（', '(', project_temp)
        project_temp = re.sub('）', ')', project_temp)
        if re.search('编号', project_temp):
            project_temp = re.sub('\(\w*编号.+\)', '', project_temp)
        if len(project_temp) > 1 and  re.search('\d', project_temp[len(project_temp) - 1]):
            project_temp = project_temp[:(len(project_temp) - 1)]
        project_return.append(project_temp.capitalize())
    return(project_return)

# 中文字典   
chs_arabic_map = {u'〇' : 0, u'一' : 1, u'二' : 2, u'三' : 3, u'四' : 4,
                  u'五' : 5, u'六' : 6, u'七' : 7, u'八' : 8, u'九' : 9,
                  u'十' : 10, u'百' : 100, u'千' : 1000, u'万' : 10000,
                  u'零' : 0, u'壹' : 1, u'贰' : 2, u'叁' : 3, u'肆' : 4,
                  u'伍' : 5, u'陆' : 6, u'柒' : 7, u'捌' : 8, u'玖' : 9,
                  u'拾' : 10, u'佰' : 100, u'仟' : 1000, u'萬' : 10000,
                  u'亿' : 10**8, u'億' : 10**8, u'幺' : 1}

def convert_chinese_digits_to_arabic(chinese_digits, chs_arabic_map):
    """
    将中文表述的数字转换成阿拉伯数字
        :param chinese_digits: 待转换的中文表达数字
        :return:转换结果
    """
    result = 0
    tmp = 0
    hnd_mln = 0
    for count in range(len(chinese_digits)):
        curr_char = chinese_digits[count]
        curr_digit = chs_arabic_map.get(curr_char, None)
        if curr_digit is not None:
            if curr_digit == 10**8:
                result = result + tmp
                result = result * curr_digit
                hnd_mln = hnd_mln*10**8 + result
                result = 0
                tmp = 0
            elif curr_digit == 10**4:
                result = result + tmp
                result = result * curr_digit
                tmp = 0
            elif curr_digit >=10:
                tmp = 1 if tmp ==0 else tmp
                result = result + curr_digit*tmp
                tmp = 0
            elif curr_digit is not None:
                tmp = tmp*10 + curr_digit
            else:
                return result
    result = result + tmp
    result = result + hnd_mln
    return (str(result) + '元')

def refine_money(str_money):
    if re.search('[零一二三四五六七八九〇壹贰叁肆伍陆柒捌玖拾佰仟萬億幺]', str_money):
        str_money = convert_chinese_digits_to_arabic(str_money, chs_arabic_map)
    money_raw = re.search('((\d*)(，|,)?)*(\d+)(\.?)(\d*)', str_money).group()
    money_raw = float(re.sub('，|,', '', money_raw))
    unit = re.search('亿|千万|百万|十万|万|千|百|十|元', str_money).group()
    if re.search('\.(\d*)', str(money_raw)):
        num_decimal = len(re.search('\.(\d*)', str(money_raw)).group(1))
    else:
        num_decimal = 0
    if unit == '亿':
        money = round(money_raw*100000000, max(num_decimal-8, 0))
    elif unit == '千万':
        money = round(money_raw*10000000, max(num_decimal-7, 0))
    elif unit == '百万':
        money = round(money_raw*1000000, max(num_decimal-6, 0))
    elif unit == '十万':
        money = round(money_raw*100000, max(num_decimal-5, 0))
    elif unit == '万':
        money = round(money_raw*10000, max(num_decimal-4, 0))
    elif unit == '千':
        money = round(money_raw*1000, max(num_decimal-3, 0))
    elif unit == '百':
        money = round(money_raw*100, max(num_decimal-2, 0))
    elif unit == '十':
        money = round(money_raw*10, max(num_decimal-1, 0))
    else:
        money = money_raw
    if money < 5000:
        return ''
    else:
        return (money)
    
def refine_up_low(str_money):
    # 对于上下限不同的金额，提取出两个不同的金额
    up_low = [x.group() for x in re.finditer('((\d*)(，|,)?)*(\d+)(\.?)(\d*)', str_money)]
    up_money = up_low[0]
    low_money = up_low[1]
    unit = re.search('亿|千万|百万|十万|万|千|百|十|元', str_money).group()
    return (refine_money(up_money + unit), refine_money(low_money + unit))

    
def refine_partya(partya):
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
    #partya = [re.sub('（', '(', x) for x in partya]
    #partya = [re.sub('）', ')', x) for x in partya]
    for i in range(len(partya)):
        if len(partya[i]) < 6:
            partya[i] = ''
    return (partya)

def refine_output_partya(partya):
    partya = [re.sub('（', '(', x) for x in partya]
    partya = [re.sub('）', ')', x) for x in partya]
    return (partya)


def refine_output_partyb(partyb):
    partyb = [re.sub('（', '(', x) for x in partyb]
    partyb = [re.sub('）', ')', x) for x in partyb]
    partyb = [re.sub('\(.*\)', '', x) for x in partyb]
    # For some case
    partyb = [re.sub('\)|）', '', x) for x in partyb]
    return (partyb)



def tiejian_key_value(soup):
    # 只匹配中国铁建
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    content_split = re.split('一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|\d、本|\d.本公司', soupcontent)
    if type(content_split) is list:
        content_split.pop(0)
    pat_partya = '公司收到(.+?)(发出的)?中标通知书'
    pat_partyb = '(子公司|、|及|和)([\w|（|）|\(|\)]+?)(公司)'
    pat_project = '中标(.+?)(，|。|；)'
    pat_money = '((\d*)(，|,)?)*(\d+)(\.?)(\d*) *(亿|千万|百万|十万|万|千|百|十)?元'
    ob_partya = []
    ob_partyb = []
    ob_project = []
    ob_contract = []
    ob_money = []
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
        content = re.sub('中标通知书', '', content)
        if re.search(pat_project, content):
            ob_project.append(re.search(pat_project, content).group(1))
        else:
            ob_project.append('')
        if re.search(pat_money, content):
            ob_money.append(refine_money(re.search(pat_money, content).group()))
        else:
            ob_money.append('')
        ob_contract.append('')
    ob_partya = refine_partya(ob_partya)
    return(zip(ob_partya, ob_partyb, ob_project, ob_contract, ob_money, ob_money, ob_combo))
  
def beiche_key_value(soup, fullname):
    # 只匹配中国北车、中国中车、中国南车
    soupcontent = re.sub('<.+>|\n|\s', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    content_split = re.split('\d、|\d.本公司', soupcontent)
    if type(content_split) is list:
        content_split.pop(0)
    pat_partya = '与(.+?)签订(了)?'
    pat_partyb = '(子公司|、|及|和)([\w|（|）|\(|\)]+?)(公司)'
    pat_contract = '签订(了)?([\w|\-|\.|，|,]+?)(合同)'
    pat_money = '((\d*)(，|,)?)*(\d+)(\.?)(\d*) *(亿|千万|百万|十万|万|千|百|十)?元'
    ob_partya = []
    ob_partyb = []
    ob_project = []
    ob_contract = []
    ob_money = []
    ob_combo = []
    for content in content_split:
        if re.search(pat_partya, content):
            ob_partya.append(re.search(pat_partya, content).group(1))
        else:
            ob_partya.append('')
        if re.search(pat_contract, content):
            contract_raw = re.search(pat_contract, content).group(2) + re.search(pat_contract, content).group(3)
            if re.search(pat_money, contract_raw):
                # 如果提取出的部分中有涉及金额
                ob_money.append(refine_money(re.search(pat_money, contract_raw).group()))
                ob_contract.append(re.split('元(的?)', contract_raw)[2])
            else:
                ob_contract.append(contract_raw)
                if re.search(pat_money, content):
                    ob_money.append(refine_money(re.search(pat_money, content).group()))
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
            
            ob_partyb.pop()
            _ = [ob_partyb.append(ob_b[0]) for x in partya]
            
            ob_combo.pop()
            _ = [ob_combo.append('') for x in partya]
            
            ob_contract.pop()
            contract_raw = re.search(pat_contract, content)
            contract = contract_raw.group(2) + contract_raw.group(3)
            if re.search(pat_money, contract):
                contract = re.split('元(的?)', contract)[2]
            contract = re.split('和|及|以及', contract)
            if len(contract) == len(partya):
                _ = [ob_contract.append(x) for x in contract]
            else:
                _ = [ob_contract.append(contract[0]) for x in partya]
            
            ob_money.pop()
            money = [x.group() for x in re.finditer(pat_money, content)]
            if len(money) == len(partya):
                _ = [ob_money.append(refine_money(x)) for x in money]
            else:
                _ = [ob_money.append(refine_money(money[0])) for x in partya]
    ob_partya = refine_partya(ob_partya)
    _ = [ob_project.append('') for x in ob_partya]
    return(zip(ob_partya, ob_partyb, ob_project, ob_contract, ob_money, ob_money, ob_combo))

def find_contract(soup):
    contract = ''
    pat_contract = '《.+?》'
    soupcontent = re.sub('<.+>|\n | ', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    section1 = str(soup.find(id = 'SectionCode_1'))
    section1 = re.sub('<.+>|\n | ', '', section1)
    section1 = re.sub('<.+>', '', section1)
    # div = soup.findAll('div')
    # re.search('合同名称：([\n]*)([\w|（|）|\(|\)|\-|—|×|\+]+)', soupcontent)
    # 2 然后在section1里找是否有带有书名号的字段
    if re.findall(pat_contract, section1):
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
                return(max(count, key = count.get))
    # 3 最后在全文里找是否有带有书名号的字段
    if re.findall(pat_contract, soupcontent[100:]):
        contract = re.findall(pat_contract, soupcontent[100:])
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
                return(max(count, key = count.get))
    # 4 全文找关键词
    if re.search('(签订了|签署了)([\w|（|）|\(|\)|\-|—|×|\+|/|《]+?)(合同|协议|合同书|协议书)', soupcontent):
            contract = re.search('(签订了|签署了)([\w|（|）|\(|\)|\-|—|×|\+|/|《]+?)(合同|协议|合同书|协议书)', soupcontent).group(2) + re.search('(签订了|签署了)([\w|（|）|\(|\)|\-|—|×|\+|/|《]+?)(合同|协议|合同书|协议书)', soupcontent).group(3)
            if len(contract) > 4:
                return(contract)
            else:
                return('')
    return('')

def find_project(soup, contract):
    project = ''
    soupcontent = re.sub('<.+>|\n | ', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    div = soup.findAll('div')
    strline = ''
    for line in div[1:]:
        # 1 在title里面找
        if line.get('title') and ('、项目名称' in line.get('title') or '、工程名称' in line.get('title') or '、中标项目' in line.get('title') or '、采购项目名称' in line.get('title')):
            if re.search('：([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)', line.get('title')):
                project = re.search('：([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)', line.get('title')).group(1)
                return(project)
            else:
                strline = line.get_text()
                strline = re.sub('\n | ', '', strline)
                strline_split = re.split('\n', strline)
                strline_split = [x for x in strline_split if len(x) > 0]
                if len(strline_split) == 1 and re.search('，', strline_split[0]) is None:
                    return (re.sub('。', '',strline_split[0]))
    for line in div[1:]:
        # 2 项目XX
        if line.get('title') and '项目' in line.get('title'):
            strline = re.sub('<.+>|\n | ', '', str(line))
            strline = re.sub('<.+>', '', strline)
            if re.search('(项目名称|工程名称|中标内容|中标名称)\w*：(\n)*([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(，|。|；|\n)', strline):
                project = re.search('(项目名称|工程名称|中标内容|中标名称)\w*：(\n)*([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(，|。|；|\n)', strline).group(3)
                return (project)        
    if re.search('(项目名称|工程名称|中标内容|中标名称)\w*：(\n)*([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(，|。|；|\n)', soupcontent):
        project = re.search('(项目名称|工程名称|中标内容|中标名称)\w*：(\n)*([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(，|。|；|\n)', soupcontent).group(3)
        # if len(project) > 7:
        return (project)
    if re.search('为([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]]+?)的?(中标单位|中标人)', soupcontent):
        project = re.search('为([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]]+?)的?(中标单位|中标人)', soupcontent).group(1)
        # if len(project) > 7:
        return (project)
    if re.search('中标项目为([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]]+?)(项目|，|。)', soupcontent):
        content = re.search('中标项目为([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]]+?)(项目|，|。)', soupcontent)
        if content.group(2) is '项目':
            project = content.group(1) + content.group(2)
        else:
            project = content.group(1)
        # if len(project) > 7:
        return (project)
    if re.search('中标([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(项目|工程|采购|活动|标段|）)', soupcontent):
        project_raw = re.findall('中标([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(项目|工程|采购|活动|标段|）)', soupcontent)
        project_raw = [x[0] + x[1] for x in project_raw]
        project_raw = [x for x in project_raw if len(x) > 7 and re.search('通知书', x) is None]
        if len(project_raw) > 0:
            len_project_raw = [len(x) for x in project_raw]
            return(project_raw[len_project_raw.index(max(len_project_raw))])
    if re.search('“([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)”', soupcontent):
        loc = [[i.start(), i.end()] for i in re.finditer('“([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)”', soupcontent)]
        content = []
        for j in range(len(loc)):
            if j == 0:
                content.append(soupcontent[max(0, loc[j][0]-5) : loc[j][1]])
            else:
                content.append(soupcontent[max(0, loc[j][0]-5, loc[j-1][1]) : loc[j][1]])
        content = [re.search('“([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(项目|采购|工程|”)', x).group() for x in content if re.search('以下简称|公示|公告|名单', x) is None and re.search('“([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+)(项目|采购|工程|”)', x)]
        content = [x for x in content if re.search('项目|采购|工程', x)]
        if len(content) > 0 and len(content[0]) > 7:
            #只取第一个
            return(content[0])
    if re.search('在([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+?)(项目|工程)中', soupcontent):
        content = re.search('在([、|\w|—|\-|~|#|·|\(|\)|（|）|\[|\]|/|\+]+?)(项目|工程)中', soupcontent)
        project = content.group(1) + content.group(2)
        if len(project) > 7:
            return (project)
    return('')

def find_money(soup):
    #pat_up_low_foreign = '((\d*)(，|,)?)*(\d+)(\.?)(\d*) *(—|\-|~)((\d*)(，|,)?)*(\d+)\.?(\d*)(亿|千万|百万|十万|万|千|百|十)?\w?元'
    pat_foreign = '((?![百千万佰仟萬亿億])[零一二三四五六七八九十百千万〇壹贰叁肆伍陆柒捌玖拾佰仟萬亿億幺]+?|((\d*)(，|,)?)*(\d+)(\.?)(\d*)(亿|千万|百万|十万|万|千|百|十)?)\w?元'
    #pat = '([零一二三四五六七八九十百千万〇壹贰叁肆伍陆柒捌玖拾佰仟萬亿億幺]+?|((\d*)(，|,)?)*(\d+)(\.?)(\d*)(亿|千万|百万|十万|万|千|百|十)?)\w?元'
    #pat_up_low = '((\d*)(，|,)?)*(\d+)(\.?)(\d*)(—|\-|~)((\d*)(，|,)?)*(\d+)\.?(\d*) *(亿|千万|百万|十万|万|千|百|十)?元'
    pat_money = '((?![百千万佰仟萬亿億])[零一二三四五六七八九十百千万〇壹贰叁肆伍陆柒捌玖拾佰仟萬亿億幺]+?|((\d*)(，|,)?)*(\d+)(\.?)(\d*)(亿|千万|百万|十万|万|千|百|十)?)元'
    soupcontent = re.sub('<.+>|\n | ', '', str(soup))
    soupcontent = re.sub('<.+?>', '', soupcontent)
    soupcontent = re.sub('=\d+', '', soupcontent) # For 250247.html
    soupcontent = re.sub('编码：\d+', '', soupcontent)
    section1 = str(soup.find(id = 'SectionCode_1'))
    section1 = re.sub('<.+>|\n | ', '', section1)
    section1 = re.sub('<.+?>', '', section1)
    section1 = re.sub('=\d+', '', section1) # For 250247.html
    section1 = re.sub('编码：\d+', '', section1)
    # 1 首先匹配合同金额上下限不一样
    #if re.search(pat_up_low_foreign, soupcontent):
      #  if re.search(pat_up_low, soupcontent):
       #     up_low_raw =  re.search(pat_up_low, soupcontent).group()
        #    up_money, low_money = refine_up_low(up_low_raw)
        #else:
         #   up_low_raw =  re.search(pat_up_low_foreign, soupcontent).group()
          #  up_money, low_money = refine_up_low(up_low_raw)
        #return (up_money, low_money)
    # 2 匹配上下限一样的金额
    div = soup.findAll('div')
    strline = ''
    for line in div[1:]:
        # 1 在title里面找
        if line.get('title') and re.search('((中标|合同)总?(金额|价))', line.get('title')):
            if re.search('：' + pat_money, line.get('title')):
                money = re.search('：' + pat_money, line.get('title')).group()
                return(refine_money(money), refine_money(money))
            else:
                strline = line.get_text()
                strline = re.sub('\n | ', '', strline)
                strline_split = re.split('\n', strline)
                strline_split = [x for x in strline_split if len(x) > 0]
                if len(strline_split) == 1 and re.search(pat_foreign, strline):
                    money = refine_money(re.search(pat_foreign, strline).group())
                    return(money, money)
    if [x.start() for x in re.finditer(pat_foreign, section1)]:
        loc = [[x.start(), x.end()] for x in re.finditer(pat_money, section1)]
        if len(loc) == 0:
            loc = [[x.start(), x.end()] for x in re.finditer(pat_foreign, section1)]
        if len(loc) > 1:
            money = []
            for j in range(len(loc)):
                if j == 0:
                    money.append(section1[max(0,loc[j][0]-20):loc[j][1]])
                else:
                    money.append(section1[max(0, loc[j][0]-20, loc[j-1][1]) : loc[j][1]])
            moneycopy = money.copy()
            for i in range(len(moneycopy)):
                if re.search('资本|资产|收入|利润|合计|总共|收款|服务费', moneycopy[i]) and re.search('中标', moneycopy[i]) is None:
                    money.remove(moneycopy[i])
                    continue
                if re.search('((中标|合同)总?(金额|价))', moneycopy[i]):
                    if i == 0 or loc[i][0]-20 > loc[i-1][1]:
                        raw_return = refine_money(re.search(pat_foreign, moneycopy[i][20:]).group())
                    else:
                        raw_return = refine_money(re.search(pat_foreign, moneycopy[i][(loc[i][0]-loc[i-1][1]):]).group())
                    return (raw_return, raw_return)
            money = [re.search(pat_foreign, x).group() for x in money if re.search(pat_foreign, x)]
            if len(money) == 0:
                return('', '')
            else:
                money = [refine_money(x) for x in money if type(refine_money(x)) is not str]
                if len(money) == 0:
                    return('', '')
                else:
                    return (max(money), max(money))
        else:
            money = section1[max(0,loc[0][0]-10):min(len(section1), loc[0][1])]
            if re.search('资本|资产|收入|利润|合计|总共|收款|服务费', money) and re.search('中标', money) is None:
                return('', '')
            else:
                money = refine_money(re.search(pat_foreign, money[10:]).group())
                return (money, money)
    elif [x.start() for x in re.finditer(pat_foreign, soupcontent)]:
        loc = [[x.start(), x.end()] for x in re.finditer(pat_money, soupcontent)]
        if len(loc) == 0:
            loc = [[x.start(), x.end()] for x in re.finditer(pat_foreign, soupcontent)]
        if len(loc) > 1:
            money = []
            for j in range(len(loc)):
                if j == 0:
                    money.append(soupcontent[max(0,loc[j][0]-20):loc[j][1]])
                else:
                    money.append(soupcontent[max(0, loc[j][0]-20, loc[j-1][1]) : loc[j][1]])
            moneycopy = money.copy()
            for i in range(len(moneycopy)):
                if re.search('资本|资产|收入|利润|合计|总共', moneycopy[i]) and re.search('中标', moneycopy[i]) is None:
                    money.remove(moneycopy[i])
                    continue
                if re.search('((中标|合同)总?(金额|价))', moneycopy[i]):
                    if i == 0 or loc[i][0]-20 > loc[i-1][1]:
                        raw_return = refine_money(re.search(pat_foreign, moneycopy[i][20:]).group())
                    else:
                        raw_return = refine_money(re.search(pat_foreign, moneycopy[i][(loc[i][0]-loc[i-1][1]):]).group())
                    return (raw_return, raw_return)
            money = [re.search(pat_foreign, x).group() for x in money if re.search(pat_foreign, x)]
            if len(money) == 0:
                return('', '')
            else:
                money = [refine_money(x) for x in money if type(refine_money(x)) is not str]
                if len(money) == 0:
                    return('', '')
                else:
                    return (max(money), max(money))
        else:
            money = soupcontent[max(0,loc[0][0]-10):min(len(soupcontent), loc[0][1])]
            if re.search('资本|资产|收入|利润|合计|总共', money) and re.search('中标', money) is None:
                return('', '')
            else:
                money = refine_money(re.search(pat_foreign, money[10:]).group())
                return (money, money)
    else:
        return('', '')