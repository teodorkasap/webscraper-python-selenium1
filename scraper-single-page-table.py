# imports
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re


# driver - browser
driver = webdriver.Chrome()

# url to be opened
url = 'https://www.ultimatetennisstatistics.com/rankingsTable'

# access website through driver
driver.get(url)

# wait
wait = WebDriverWait(driver, 10)

# click the button "20" to show dropdown options to display records per page
item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//span[@class='dropdown-text' and contains(.,'20')]")))
driver.execute_script("arguments[0].click();", item)

# click the option "all" in the dropdown
item = wait.until(EC.visibility_of_element_located(
    (By.XPATH, "//a[@class='dropdown-item dropdown-item-button' and contains(.,'All')]")))
driver.execute_script("arguments[0].click();", item)

# pause for table to be loaded
time.sleep(2)

# define a list to hold all player id values
player_ids = []


# scrape the table data
for table in driver.find_elements_by_xpath('//*[contains(@id,"rankingsTable")]//tr'):
    # the line below gets the data on each row as an array
    #data = [item.text for item in table.find_elements_by_xpath(".//*[self::td or self::th]")]
    data = table.get_attribute('innerHTML')
    match = re.search('playerId=(\d+)', data)
    if match:
        player_id=match.group(1)
        player_ids.append(player_id)

print(player_ids)
