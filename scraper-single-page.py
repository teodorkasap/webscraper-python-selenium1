# imports
from selenium import webdriver
import pandas as pd

# driver - browser
driver = webdriver.Chrome()

# access website through driver
driver.get('https://forums.edmunds.com/discussion/2864/general/x/entry-level-luxury-performance-sedans/p702')

# extract username from the page
userid_element = driver.find_elements_by_xpath('//*[@id="Comment_5561090"]/div/div[2]/div[1]/span[1]/a[2]')[0]
userid = userid_element.text
print(userid)

# extract date from the page
user_date = driver.find_elements_by_xpath('//*[@id="Comment_5561090"]/div/div[2]/div[2]/span[1]/a/time')[0]
date = user_date.get_attribute('title')
print(date)

# extract comments from the page
user_message = driver.find_elements_by_xpath('//*[@id="Comment_5561090"]/div/div[3]/div/div[1]')[0]
comment = user_message.text
print(comment)