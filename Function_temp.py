# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 10:02:52 2018

@author: 25008

This is a Temp file for the function match project contract and value
"""
def refine_contract():


def refine_project():
    
    
def refine_money(str_money):
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

def match_contract():
    

def match_project():
    

def match_money():
