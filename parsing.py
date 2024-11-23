import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def parseLink():
    options = Options()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    browser.get("https://www.minsport.gov.ru/activity/government-regulation/edinyj-kalendarnyj-plan/")
    parent_element = browser.find_element("id", "sId-251")
    inner_element = parent_element.find_element("xpath", ".//*[text()='2024']")
    inner_element.click()
    download_link = parent_element.find_element("xpath", ".//*[text()='Скачать документ']")
    href_value = download_link.get_attribute('href')
    browser.quit()
    return href_value