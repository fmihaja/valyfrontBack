from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import time
import random
from dataclasses import dataclass
from typing import List
from datetime import datetime

# @dataclass
# class dataTH:
#     Time: str
#     Cur: str
#     Imp: str
#     Event: str
#     Actual: str
#     Forecast: str
#     Previous: str

@dataclass
class dataGeo:
    img: str
    desc: str

# Configuration de Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=1920,1080")

# Chemin vers ChromeDriver
service = Service(executable_path="chromedriver.exe")

# Tentative de connexion avec retry
max_retries = 3
retry_delay = 5
data: List[dataGeo] = []
# idCountry = [25, 6, 72, 43, 4, 35, 12, 5]

for attempt in range(max_retries):
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(400)
        driver.get("https://www.reuters.com/world/")
        time.sleep(random.uniform(1, 3))
        break
    except (TimeoutException, WebDriverException) as e:
        print(f"Tentative {attempt + 1} échouée : {e}")
        if 'driver' in locals():
            driver.quit()
        time.sleep(retry_delay)
else:
    raise Exception("Échec du chargement après plusieurs tentatives")

wait = WebDriverWait(driver, 20)

try:
    divCards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "story-card")))
    for divCard in divCards:
        img = divCard.find_element(By.CSS_SELECTOR, "img")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        src = img.get_attribute("src")
                    # Si src est None, essayer d'autres attributs
        if not src:
            src = img.get_attribute("data-src")  # Pour les images lazy loading
        if not src:
                src = img.get_attribute("data-lazy-src")  # Autre attribut common
        txt = divCard.find_element(By.CLASS_NAME, "media-story-card-module__body__nZjo1")
        geo_data = dataGeo(img=src or "", desc=txt.text.strip())
        data.append(geo_data)
    print("scarping fait")
    for i in data:
        print(i.img+"\n description: "+i.desc+"\n")
except TimeoutException: 
    print("erreur")
time.sleep(2)
driver.quit()
# Attendre que la page soit interactive