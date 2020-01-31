import os
import pandas as pd
import googlemaps
import time
import requests, json
import numpy as np
from path import *

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common.exceptions import *

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

gmaps = googlemaps.Client(key=api_key)

def isNaN(num):
    return num == ""

def get_inner_html(element):
    return element.get_attribute('innerHTML')

def get_outer_html(element):
    return element.get_attribute('outerHTML')

def wait_element(driver, selector, second = 10):
    return WebDriverWait(driver,second).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

column = {0:'city', 1:'country', 2:'update_time', 3:'confirm', 4:'death', 5:'recover'}

if __name__ == "__main__":
    df=None

    #try:    
    #    df = pd.read_csv(csv_path, encoding='utf-8', index_col=0)
    #except:
    df = pd.DataFrame({'city':[], 'country':[], 'long':[], 'lat':[], 'update_time':[], 'confirm':[], 'death':[], 'recover':[]})

    driver = webdriver.Chrome(chrome_path, options=options)
    driver.implicitly_wait(3)
    driver.get(web_path)

    body = wait_element(driver, 'tbody')
    trs = body.find_elements_by_css_selector('tr')
    
    df_index = 0
    for tr in trs[:]:
        tds = tr.find_elements_by_css_selector('td')

        for idx, td in enumerate(tds):
            df.loc[df_index, [column[idx]]] = td.text

        lng = df.loc[df_index, 'long']
        lat = df.loc[df_index, 'lat']
        if not (lng != lng and lat != lat):
            print("continue")
            continue

        city = df.loc[df_index, [column[0]]].item()
        country = df.loc[df_index, [column[1]]].item()

        location = city if city else country

        try:
            geo = gmaps.geocode(location)[0]['geometry']['location']
            df.loc[df_index, 'long'] = f"{geo['lng']:0.7f}" #long
            df.loc[df_index, 'lat'] = f"{geo['lat']:0.7f}" #lat
        except Exception as e:
            print(e)
            pass

        df_index+=1

    df.to_csv(csv_path, encoding='utf-8')
    driver.quit()
    
    j = {'data':[]}
    for index in range(1, len(df)):
        temp = {
            "id":index,
            "city": "" if isNaN(df.loc[index,'city']) else df.loc[index,'city'],
            "country": df.loc[index,'country'],
            "long": df.loc[index,'long'],
            "lat": df.loc[index,'lat'],
            "update_time": df.loc[index,'update_time'],
            "confirm": 0 if isNaN(df.loc[index,'confirm']) else df.loc[index,'confirm'],
            "death": 0 if isNaN(df.loc[index,'death']) else df.loc[index,'death'],
            "recover": 0 if isNaN(df.loc[index,'recover']) else df.loc[index,'recover']
        }

        j['data'].append(temp)

    j = json.dumps(j)
    #print(j)

    headers = {'x-api-key': f'{x_api_key}'}
    res = requests.post(end_point,data=j,headers=headers)
    print(res.raise_for_status)


