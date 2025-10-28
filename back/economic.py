import os
import sys
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

@dataclass
class dataTH:
    Time: str
    Cur: str
    Imp: str
    Event: str
    Actual: str
    Forecast: str
    Previous: str

@dataclass
class dateTD:
    date: str
    tab: List[dataTH]

def close_popup(driver, wait, timeout=3):
    """Ferme le popup s'il apparaît pendant `timeout` secondes"""
    try:
        closeButton = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".popupCloseIcon.largeBannerCloser"))
        )
        closeButton.click()
        print("Popup fermé")
        time.sleep(1)
        return True
    except TimeoutException:
        return False

def close_breaking_news(driver, wait, timeout=3):
    """Ferme la bannière breaking news si présente"""
    try:
        close_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".breakingNewsClose"))
        )
        close_button.click()
        print("Bannière breaking news fermée")
        time.sleep(1)
        return True
    except TimeoutException:
        return False

def export_sections_by_date(data: List[dateTD]):
    """Exporte les données avec sections groupées par date dans un seul onglet"""
    base_path = r"C:\Users\Afa-tech\Desktop\disque_dur\EMIT\code\valt\front\valy\src\assets"
    download_folder = os.path.join(base_path, "economie")
    os.makedirs(download_folder, exist_ok=True)
    
    filename = f"economic_calendar_sections.xlsx"
    filepath = os.path.join(download_folder, filename)
    
    all_rows = []
    total_events = 0
    
    print("\n" + "="*60)
    print(" CRÉATION DES SECTIONS PAR DATE")
    print("="*60)
    
    for i, day_data in enumerate(data):
        if day_data.tab:
            date_header = f"=== {day_data.date} ==="
            all_rows.append([date_header, '', '', '', '', '', ''])
            
            print(f" {day_data.date}: {len(day_data.tab)} événements")
            
            for event in day_data.tab:
                all_rows.append([
                    event.Time,
                    event.Cur,
                    event.Imp,
                    event.Event,
                    event.Actual,
                    event.Forecast,
                    event.Previous
                ])
                total_events += 1
            
            if i < len(data) - 1:
                all_rows.append(['', '', '', '', '', '', ''])
    
    if all_rows:
        df_all = pd.DataFrame(all_rows, columns=[
            'Time', 'Currency', 'Impact', 'Event', 
            'Actual', 'Forecast', 'Previous'
        ])
        
        try:
            df_all.to_excel(filepath, index=False, sheet_name='Economic Calendar')
            
            print("\n" + "="*60)
            print(" EXPORT TERMINÉ")
            print("="*60)
            print(f" Fichier créé: {filename}")
            print(f" Chemin complet: {filepath}")
            print(f" Total événements: {total_events}")
            
            return filepath
            
        except Exception as e:
            print(f" Erreur lors de l'export Excel: {e}")
            return None
    else:
        print(" Aucune donnée à exporter")
        return None

def scrape_economic_calendar():
    """Fonction principale pour scraper le calendrier économique"""
    
    # Configuration de Chrome
    chrome_options = webdriver.ChromeOptions()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    # chrome_options.add_argument('--headless')  # Décommentez pour mode headless
    
    service = Service(executable_path="chromedriver.exe")
    
    max_retries = 3
    retry_delay = 5
    data: List[dateTD] = []
    idCountry = [25, 6, 72, 43, 4, 35, 12, 5]
    driver = None
    
    # Tentative de connexion
    for attempt in range(max_retries):
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(400)
            driver.get("https://www.investing.com/economic-calendar")
            break
        except (TimeoutException, WebDriverException) as e:
            print(f"Tentative {attempt + 1} échouée : {e}")
            if driver:
                driver.quit()
            time.sleep(retry_delay)
    else:
        raise Exception("Échec du chargement après plusieurs tentatives")
    
    try:
        wait = WebDriverWait(driver, 20)
        
        # GMT selection
        try:
            gmt = wait.until(EC.element_to_be_clickable((By.ID, "economicCurrentTime")))
            close_popup(driver, wait)
            close_breaking_news(driver, wait)
            driver.execute_script("arguments[0].click();", gmt)
            print("heure gmt cliquée")
            
            try:
                InstabulGmt = wait.until(EC.element_to_be_clickable((By.ID, "liTz63")))
                close_popup(driver, wait)
                close_breaking_news(driver, wait)
                driver.execute_script("arguments[0].click();", InstabulGmt)
                print("heure Istanbul gmt cliquée")
            except TimeoutException: 
                print("Aucun Istanbul gmt")
        except TimeoutException: 
            print("Aucun gmt")
        
        # Filtrage
        try:
            filtrage = wait.until(EC.element_to_be_clickable((By.ID, "filterStateAnchor")))
            close_popup(driver, wait)
            close_breaking_news(driver, wait)
            driver.execute_script("arguments[0].click();", filtrage)
            print("filtrage cliqué")
            
            countryClearAll = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Clear")))
            close_popup(driver, wait)
            close_breaking_news(driver, wait)
            driver.execute_script("arguments[0].click();", countryClearAll)
            print("clear all cliqué")
            
            for i in idCountry:
                country = "country" + str(i)
                countrySelected = wait.until(EC.element_to_be_clickable((By.ID, country)))
                time.sleep(random.uniform(1, 2))
                close_popup(driver, wait)
                close_breaking_news(driver, wait)
                driver.execute_script("arguments[0].click();", countrySelected)
                print(f"id country : {i} cliqué")
            
            importance = wait.until(EC.element_to_be_clickable((By.ID, "importance3")))
            close_popup(driver, wait)
            close_breaking_news(driver, wait)
            driver.execute_script("arguments[0].click();", importance)
            print("Selection niveau checked")
            
            submit = wait.until(EC.element_to_be_clickable((By.ID, "ecSubmitButton")))
            close_popup(driver, wait)
            close_breaking_news(driver, wait)
            driver.execute_script("arguments[0].click();", submit)
            print("requête envoyée")
            
            thisWeek = wait.until(EC.element_to_be_clickable((By.ID, "timeFrame_thisWeek")))
            close_popup(driver, wait)
            close_breaking_news(driver, wait)
            driver.execute_script("window.scrollTo(0, 0);")
            driver.execute_script("arguments[0].click();", thisWeek)
            print("this week cliqué")
            
            time.sleep(3)
            
        except TimeoutException as e:
            print(f"Erreur filtrage: {e}")
        
        # Récupération des données
        try:
            table = wait.until(EC.visibility_of_element_located((By.ID, "economicCalendarData")))
            
            current_date_data = None
            tr_elements = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
            
            for tr in tr_elements:
                date_td = tr.find_elements(By.CSS_SELECTOR, "td.theDay")
                if date_td:
                    current_date_data = dateTD(date=date_td[0].text.strip(), tab=[])
                    data.append(current_date_data)
                    print(f"Date trouvée: {date_td[0].text.strip()}")
                else:
                    tds = tr.find_elements(By.CSS_SELECTOR, "td")
                    if len(tds) >= 7 and current_date_data is not None:
                        current_date_data.tab.append(
                            dataTH(
                                Time=tds[0].text.strip() if tds[0].text.strip() else "",
                                Cur=tds[1].text.strip() if tds[1].text.strip() else "",
                                Imp=tds[2].text.strip() if tds[2].text.strip() else "",
                                Event=tds[3].text.strip() if tds[3].text.strip() else "",
                                Actual=tds[4].text.strip() if tds[4].text.strip() else "0",
                                Forecast=tds[5].text.strip() if tds[5].text.strip() else "",
                                Previous=tds[6].text.strip() if tds[6].text.strip() else ""
                            )
                        )
            
            print(f"Nombre de jours trouvés: {len(data)}")
            
        except TimeoutException:
            print("Erreur lors de la récupération du tableau")
        except Exception as e:
            print(f"Erreur inattendue: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    # Export des données
    if data:
        filepath = export_sections_by_date(data)
        if filepath:
            print(f"\n Fichier créé: {filepath}")
            return True
        else:
            print("\n Échec de la création du fichier")
            return False
    else:
        print(" Aucune donnée collectée pour l'export")
        return False

# Pour exécution directe
if __name__ == "__main__":
    success = scrape_economic_calendar()
    sys.exit(0 if success else 1)