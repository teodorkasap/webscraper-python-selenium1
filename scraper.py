# imports
from selenium import webdriver
import pandas as pd
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

import time
import re
import os


# driver - browser
driver = webdriver.Chrome()

# url to be opened
url = 'https://www.ultimatetennisstatistics.com/rankingsTable'
url2 = 'https://www.ultimatetennisstatistics.com/playerProfile?playerId='

# access website through driver / 
driver.get(url)

# wait / bekle tanımlıyoruz, birinci parametre sürücü ikincisi ise 'timeout'
wait = WebDriverWait(driver, 60)

# click the button "20" to show dropdown options to display records per page
item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//span[@class='dropdown-text' and contains(.,'20')]")))
driver.execute_script("arguments[0].click();", item)

# click the option "all" in the dropdown
item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//a[@class='dropdown-item dropdown-item-button' and contains(.,'All')]")))
driver.execute_script("arguments[0].click();", item)

# pause for table to be loaded
time.sleep(0.5)

# define a list to hold all player id values
player_ids = []


players_master_dataframe_list=[]

# scrape the table data / ranking listesi tablosunu tarama
for table in driver.find_elements_by_xpath('//*[contains(@id,"rankingsTable")]//tr'):
    # the line below gets the data on each row as an array
    #data = [item.text for item in table.find_elements_by_xpath(".//*[self::td or self::th]")]

    # find html links in the scraped table / tablonun arka planındaki html linklerini alma ve oradan playerID değişkenini bulma
    data = table.get_attribute('innerHTML')
    match = re.search('playerId=(\d+)', data)

    # adding playerId's found to list / bulduğumuz playerId'leri bir listede topluyoruz
    if match:
        player_id=match.group(1)
        player_ids.append(player_id)

print(player_ids)

# pause for table to be loaded / her ihtimale karşı, html elemanlarının yüklenmesini bekleme
driver.implicitly_wait(0.5)

# loop over the list of player ids, define range first / oyuncuların bulunduğu listenin üzerinden geçerek, 
# url leri oluşturup, açılan sayfaları taramaya başlıyoruz.
for i in range(0,500):

    # compose url's for player detail pages and open these url's / url'ye aşağıdaki gibi playerId yi ekliyoruz ve sayfayı açıyoruz
    driver.get(url2+player_ids[i])

    # get player name / oyuncunun ismini alıp, "player_name" değişkenine atıyoruz
    item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//h3")))
    player_name=item.text
    print(' ')
    print('****************')
    print(player_name) 
    print(' ')
    print('****************')

    # open dropdown for statistics options / filtreleme yapan "dropdown" menü elemanına tıklayıp istediğimiz
    # filtrelemeyi yapıyoruz.
    item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//ul[@id='playerPills']/li[9]/a[@class='dropdown-toggle' and contains(.,'Statistics')]")))
    driver.execute_script("arguments[0].click();", item)

    # select the statistics page from the dropdown / istatistikler seçeneğine tıklama
    item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//a[@id='statisticsPill']")))
    driver.execute_script("arguments[0].click();", item)
    
    # pause for selection to be loaded / buraya her ihtimale karşı bir bekleme ekledim
    driver.implicitly_wait(0.5)

    # select the "Adv."  dropdown and click it / ileri seviye filtreleme seçeneklerini göstermek için "Adv." elemanına tıklıyoruz
    item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//div[@id='statistics']/div/div[7]/div/button[@class='btn btn-primary' and contains(.,'Adv.')]")))
    driver.execute_script("arguments[0].click();", item)

    # pause just in case / yine kısa bir bekleme, sayfa tam olarak yüklensin diye
    driver.implicitly_wait(0.5)

    # input stats "from" date to get the relevant data tables / filtreleme elemanlarına son 3 ayın 
    # performans istatistiklerini görebilmek için girilen filtreleme bilgileri
    item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//input[@id='statsFromDate']")))
    item.send_keys('01-03-2019')
    
    # pause just in case / yine kısa bir bekleme
    driver.implicitly_wait(0.5)

    # def. an empty list to hold player data / boş bir liste tanımadık,
    # bunu biraz sonra oyuncu istatistiklerini tutmak için kullanacağız
    player_data = []
    # scrape the table with player stats, as text first, then append to list as "list of lists" /
    # oyuncu istatistiklerini sayfadan aşağıdaki "for" döngüsü ile kazıyoruz
    for table in driver.find_elements_by_xpath('//*[contains(@id,"playerStatsTab")]//tr'):
        driver.implicitly_wait(0.5)
        try:
            data = [item.text for item in table.find_elements_by_xpath(".//*[self::td or self::th]")]
        except StaleElementReferenceException:
            pass

    # for table in wait.until(EC.visibility_of_all_elements_located((By.XPATH,'//*[contains(@id,"playerStatsTab")]//tr'))):
    #     data = [item.text for item in table.find_elements_by_xpath(".//*[self::td or self::th]")]
        
        # scraped data appended to the empty list define earlier /
        # oyuncu detay sayfasındaki bilgileri liste halinde , yukarıda tanımladığımız 
        # listeye kaydediyoruz (her elemanı liste olan bir liste oluyor elimizde)
        player_data.append(data)
    
    # check console output / listeyi konsola yazdırıp kontrol edelim
    print(player_data)

    # turn the "list of lists" to data frame / listeyi bir 'dataframe'e çeviriyoruz (pandas kullanarak)
    data_frame=pd.DataFrame(player_data)
    print(' ')
    print(' ')
    print(data_frame)

    # Defensive coding: in case the statistics are not found on the page /
    # Aşağıdaki if döngüsü, istatistikleri döndüremezsek (sayfada bir hata veya eksik olması durumu)
    # programın yarı yolda patlamasına engel oluyor.
    if not data_frame.empty:
        # choose relevant columns and save as data frame / işimize yarayan satırları seçtik ve bir dataframe olarak
        # kaydettik
        data_frame=data_frame.iloc[[3,6,8,13,14],[0,1]]
        print(' ')
        print(' ')
        print(data_frame)

        # transpose dataframe / 'dataframe'i yan çevirdik 
        # seçtiğimiz satırlar artık sütun haline geldi
        data_frame = data_frame.T
        columns = ['1st Serve' ,  'Break Points Saved' ,  'Service Games Won' ,  '2nd Srv. Return Won' ,  'Break Points Won' ]
        data_frame.columns=columns
        data_frame=data_frame.drop(data_frame.index[0:1])
        # Change all dtypes to float for calculations in later stages /
        # Sütunlardaki bilgileri , float haline getirdik, bu sayede sonrasında hesaplamalarda
        # kullanabileceğiz
        for col in columns:
            data_frame[col]=data_frame[col].str.replace('%','')
            data_frame[col]=data_frame[col].astype(float, errors='ignore')
        
        # insert scraped info into data frame /
        # kazıdığımız oyuncu adı bilgisini de 'data_frame'e ekliyoruz
        data_frame.insert(0,'Player Name',player_name)
        print(' ')
        print(' ')
        print(data_frame)
        print(data_frame.dtypes)
        # save all data frames to master list /
        # elimizdeki tek satırlık 'data_frame'i projenin başında tanımladığımız,
        # tüm bilgileri içerecek olan players_master_dataframe_list adlı listeye ekliyoruz
        players_master_dataframe_list.append(data_frame)

# Check the list of data frames /
# Data frame listesini bir kontrol edelim
print(players_master_dataframe_list)

# Concat all data frames in list into one data frame /
# Listedeki tüm data frame objelerini birleştirip , nihayi bir data frame elde ediyoruz.
players_master_dataframe=pd.concat(players_master_dataframe_list)


# if needed, we can save to disc as csv file /
# ihtiyaç halinde csv olarak, aşağıdaki kod bloku ile kaydedebiliriz
filename = 'player_stats.txt'

if not os.path.isfile(filename):
   players_master_dataframe.to_csv(filename, sep=' ',index=False)
else: 
   players_master_dataframe.to_csv(filename, mode='a', header=False, sep=' ',index=False)
