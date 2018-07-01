# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 11:36:38 2018

@author: 25008
"""

import os 
import csv
import numpy as np
import pandas as pd
import jieba
import jieba.posseg



os.chdir('')
file = open('/hetong.train', 'r', encoding = 'utf-8-sig')
hetong_train = csv.reader(file, delimiter = '\t')
hetong_train = list(hetong_train)
file.close()
hetong_train = pd.DataFrame(hetong_train, columns = ['公告id','甲方','乙方','项目名称','合同名称','合同金额上限','合同金额下限','联合体成员'])

# 甲方、乙方的结尾词
# jiagongsi = np.array(hetong_train['甲方']).tolist()
# jialast = [x(len(x)-1) for x in jiagongsi if x]


df_partya_cixing = pd.DataFrame(columns = ['甲方', '甲方词性'])
ll = []
ss = []
for i in hetong_train['甲方']:
    seg = jieba.posseg.cut(i) 
    l = []
    s = [] 
    for i in seg: 
        l.append(i.word)
        s.append(i.flag)
    ll.append('/'.join(l))
    ss.append('/'.join(s))
df_partya_cixing['甲方'] = ll
df_partya_cixing['甲方词性'] = ss
writer = pd.ExcelWriter('partya_cixing.xlsx')
df_partya_cixing.to_excel(writer, 'page_1', float_format = '%.5f', index = False, encoding = 'gbk')
writer.save()


end_raw = [jieba.lcut(x).pop() for x in hetong_train['甲方'] if x]
end_raw = list(set(end_raw))
