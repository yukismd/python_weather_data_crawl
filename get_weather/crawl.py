# -*- coding: utf-8 -*-
"""
Created on Sat May  2 01:53:36 2020

@author: Yuki Shimada

気象庁ページからの天候データ取得
"""

import pandas as pd
import numpy as np
from selenium import webdriver


def get_one_location_one_day_weather(point_num, prec_no, block_no, year, month, day):
    """
    1観測Point指定する日の24時間天候データを返す

    Ex: get_one_location_one_day_weather(point_num=620, prec_no=44, block_no=47662, year=2020, month=1, day=10)
    
    Parameters
    --------------
    point_num : int or float
        観測所番号（都道府県番号と都市番号で特定されるので、単に識別IDとして利用。ページへのアクセスには利用されない）
    prec_no : int or float
        都道府県番号
    block_no : int or float
        都市番号
    year : int
    month : int
    day : int
    
    Returns
    --------------
    data_1day : padas.DataFrame
        ある観測地点の1日分のデータ（24*21）
    """
    
    point_num = int(point_num)
    prec_no = int(prec_no)
    block_no = int(block_no)
    year = int(year)
    month = int(month)
    day = int(day)
    
    header = ['現地気圧(hPa)', '海面気圧(hPa)', '降水量(mm)', '気温(℃)', '露点温度(℃)', '蒸気圧(hPa)', 
              '湿度(％)', '風速(m/s)', '風向', '日照時間(h)', '全天日射量(MJ/㎡)', '降雪', '積雪', 
              '天気', '雲量', '視程(km)']
    
    print("Point:{}, 都道府県:{}, 都市:{}, Year:{}, Month:{}, Day:{}".format(point_num, prec_no, block_no, year, month, day))
    
    browser = webdriver.Chrome()
    # prec_no,block_no,year,month,dayをパラメータとし、クローリング対象ページへアクセス
    page_url = 'https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php'
    browser.get(page_url+"?prec_no=%s&block_no=%s&year=%s&month=%s&day=%s&view=" % (prec_no, block_no, year, month, day))
    
    elems = browser.find_elements_by_class_name('data_0_0')
    list_1d = np.array([elem.text for elem in elems])
    list_2d = list_1d.reshape((24,16))    # ページのテーブルを2D Arrayで格納（24時間×16カラム(len(header))）
    
    data_1day = pd.DataFrame(list_2d, columns=header)
    data_1day['year'] = year
    data_1day['month'] = month
    data_1day['day'] = day
    data_1day['time'] = np.arange(24)+1
    data_1day['point_number'] = point_num
    
    browser.quit()

    return data_1day


def get_one_location_all_day_weather(point_num, prec_no, block_no, year_month_day):
    """
    1観測Point指定する日の24時間天候データを返す

    Parameters
    --------------
    point_num : int or float
        観測所番号（都道府県番号と都市番号で特定されるので、単に識別IDとして利用。ページへのアクセスには利用されない）
    prec_no : int or float
        都道府県番号
    block_no : int or float
        都市番号
    year_month_day : list
        [(2020, 1, 1), (2020, 1, 2), (2020, 1, 3),...]
    
    Returns
    --------------
    data_all_day : padas.DataFrame
        ある観測地点の指定する日数分のデータ（日数分*21）
    """
    
    data_all_day = pd.DataFrame()
    
    for y_m_d in year_month_day:
        data_1day = get_one_location_one_day_weather(point_num=point_num, prec_no=prec_no, block_no=block_no, 
                                                     year=y_m_d[0], month=y_m_d[1], day=y_m_d[2])
        
        if data_all_day.shape[0] == 0:
            data_all_day = data_1day
        else:
            data_all_day = pd.concat([data_all_day, data_1day])
    
    return data_all_day
