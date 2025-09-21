from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import time
import random
# Configuration de Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=1920,1080")

# Chemin vers ChromeDriver (vérifie la version !)
service = Service(executable_path="chromedriver.exe")

# Tentative de connexion avec retry
max_retries = 3
retry_delay = 5

idCountry=[ 25,6,72,43,4,35,12,5]

for attempt in range(max_retries):
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(400)  # Timeout pour le chargement des pages
        driver.get("https://www.investing.com/economic-calendar")
        break  # Si réussi, sortir de la boucle
    except (TimeoutException, WebDriverException) as e:
        print(f"Tentative {attempt + 1} échouée : {e}")
        driver.quit()
        time.sleep(retry_delay)
else:
    raise Exception("Échec du chargement après plusieurs tentatives")

# Attendre que la page soit interactive
wait = WebDriverWait(driver, 20)

#fermer pop up
def close_popup(driver, wait, timeout=3):
    """Ferme le popup s'il apparaît pendant `timeout` secondes"""
    try:
        closeButton = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".popupCloseIcon.largeBannerCloser"))
        )
        closeButton.click()
        print("Popup fermé")
        time.sleep(1)  # petit délai après fermeture
        return True
    except TimeoutException:
        return False
#choisir le gmt
try:
    gmt=wait.until(EC.element_to_be_clickable((By.ID, "economicCurrentTime")))
    close_popup(driver, wait)
    gmt.click()
    print("heure gmt cliquer")
    try:
        InstabulGmt=wait.until(EC.element_to_be_clickable((By.ID, "liTz63")))
        time.sleep(random.uniform(3, 10))
        close_popup(driver, wait)
        InstabulGmt.click()
        print("heure Instabul gmt cliquer")
    except TimeoutException: 
        print("Aucun instabul gmt")
except TimeoutException: 
    print("Aucun gmt")

#filtrage
try:
    filtrage = wait.until(EC.element_to_be_clickable((By.ID, "filterStateAnchor")))
    time.sleep(random.uniform(3, 10))
    close_popup(driver, wait)
    filtrage.click()
    print("filtrage cliquer")
    try:
        countryClearAll = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Clear")))
        time.sleep(random.uniform(3, 10))
        close_popup(driver, wait)
        countryClearAll.click()
        print("clear all cliquer")
        try:
            print()
            for i in idCountry:
                country="country"+str(i)
                countrySelected=wait.until(EC.element_to_be_clickable((By.ID, country)))
                time.sleep(random.uniform(3, 10))
                close_popup(driver, wait)
                countrySelected.click()
                print("id country : "+str(i)+" cliquer")
        except TimeoutException:
            print("Erreur d'id country")
        try:
            importance=wait.until(EC.element_to_be_clickable((By.ID, "importance3")))
            time.sleep(random.uniform(3, 10))
            close_popup(driver, wait)
            importance.click()
            print("Selection niveau checked")
        except TimeoutException:
            print("Erreur de selection niveau")
    except TimeoutException:
        print("Erreur de clear")
    #envoie du requete
    try:
        submit=wait.until(EC.element_to_be_clickable((By.ID, "ecSubmitButton")))
        time.sleep(random.uniform(3, 10))
        close_popup(driver, wait)
        submit.click()
        print("renvoie de requete")
    except TimeoutException:
        print("Erreur de renvoie de requete")

except TimeoutException:
    print("Aucun filtrage trouvé")
time.sleep(50)
driver.quit()
