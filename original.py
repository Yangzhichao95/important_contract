# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 22:25:12 2018

@author: 25008
"""

from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import *
import re
import os
import warnings
import pandas as pd
# import tabular

path = 'D:/Tianchi/data/round1_train_20180518/重大合同/pdf/'
#df = pd.DataFrame(columns=['公告id','股东全称','股东简称','变动截至日期','变动价格','变动数量','变动后持股数','变动后持股比例'])
i = 0
lst = []
for i in os.listdir(path):
    lst.append(i)
    
# for filename in lst:
 #   try:
filename = lst[0]
path1 = path + filename
print(filename)
fp = open(path1, 'rb')
#用文件对象来创建一个pdf分析器
parser = PDFParser(fp)
#创建一个PDF文档
doc = PDFDocument(parser)


rsrcmgr = PDFResourceManager(caching=False)
#创建一个PDF设备对象
laparams = LAParams()
#创建一个PDF页面聚合对象
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#创建一个PDF解析对象
interpreter = PDFPageInterpreter(rsrcmgr, device)

for page in PDFPage.create_pages(doc):
    interpreter.process_page(page)
    #接受该页面的LTPage对象
    layout=device.get_result()
    #这里layout是一个LTPage对象，里面存放着这个page解析出的各种对象
    l = []
    for x in layout:
        #如果x是水平文本对象的话
        if(isinstance(x, LTTextBoxHorizontal)):
            l.append(x.get_text())
    s=''.join(l).replace('\n','')
    

