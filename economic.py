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
data: List[dateTD] = []
idCountry = [25, 6, 72, 43, 4, 35, 12, 5]

for attempt in range(max_retries):
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(400)
        driver.get("https://www.investing.com/economic-calendar")
        break
    except (TimeoutException, WebDriverException) as e:
        print(f"Tentative {attempt + 1} échouée : {e}")
        if 'driver' in locals():
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
        time.sleep(1)
        return True
    except TimeoutException:
        return False

# Fermer aussi la bannière breaking news
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

# choisir le gmt
try:
    gmt = wait.until(EC.element_to_be_clickable((By.ID, "economicCurrentTime")))
    close_popup(driver, wait)
    close_breaking_news(driver, wait)
    driver.execute_script("arguments[0].click();", gmt)
    print("heure gmt cliquée")
    
    try:
        InstabulGmt = wait.until(EC.element_to_be_clickable((By.ID, "liTz63")))
        time.sleep(random.uniform(1, 3))
        close_popup(driver, wait)
        close_breaking_news(driver, wait)
        driver.execute_script("arguments[0].click();", InstabulGmt)
        print("heure Istanbul gmt cliquée")
    except TimeoutException: 
        print("Aucun Istanbul gmt")
except TimeoutException: 
    print("Aucun gmt")

#filtrage
try:
    filtrage = wait.until(EC.element_to_be_clickable((By.ID, "filterStateAnchor")))
    time.sleep(random.uniform(1, 3))
    close_popup(driver, wait)
    close_breaking_news(driver, wait)
    driver.execute_script("arguments[0].click();", filtrage)
    print("filtrage cliqué")
    
    try:
        countryClearAll = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Clear")))
        time.sleep(random.uniform(1, 3))
        close_popup(driver, wait)
        close_breaking_news(driver, wait)
        driver.execute_script("arguments[0].click();", countryClearAll)
        print("clear all cliqué")
        
        try:
            for i in idCountry:
                country = "country" + str(i)
                countrySelected = wait.until(EC.element_to_be_clickable((By.ID, country)))
                time.sleep(random.uniform(1, 2))
                close_popup(driver, wait)
                close_breaking_news(driver, wait)
                driver.execute_script("arguments[0].click();", countrySelected)
                print(f"id country : {i} cliqué")
        except TimeoutException:
            print("Erreur d'id country")
            
        try:
            importance = wait.until(EC.element_to_be_clickable((By.ID, "importance3")))
            time.sleep(random.uniform(1, 3))
            close_popup(driver, wait)
            close_breaking_news(driver, wait)
            driver.execute_script("arguments[0].click();", importance)
            print("Selection niveau checked")
        except TimeoutException:
            print("Erreur de selection niveau")
            
    except TimeoutException:
        print("Erreur de clear")
    
    #envoie du requete
    try:
        submit = wait.until(EC.element_to_be_clickable((By.ID, "ecSubmitButton")))
        time.sleep(random.uniform(1, 3))
        close_popup(driver, wait)
        close_breaking_news(driver, wait)
        driver.execute_script("arguments[0].click();", submit)
        print("requête envoyée")
    except TimeoutException:
        print("Erreur d'envoi de requête")
    
    #selection de cette semaine
    try:
        thisWeek = wait.until(EC.element_to_be_clickable((By.ID, "timeFrame_thisWeek")))
        time.sleep(random.uniform(1, 3))
        close_popup(driver, wait)
        close_breaking_news(driver, wait)
        driver.execute_script("window.scrollTo(0, 0);")
        driver.execute_script("arguments[0].click();", thisWeek)
        print("this week cliqué")
        
        # Attendre que le tableau se mette à jour
        time.sleep(3)
        
    except TimeoutException:
        print("Erreur this week cliqué")
    
    try:
        # recuperation des titre du tableau
        table = wait.until(EC.visibility_of_element_located((By.ID, "economicCalendarData")))
        th_elements = table.find_elements(By.CSS_SELECTOR, "thead > tr > th")
        
        print("En-têtes du tableau:")
        for th in th_elements:
            print(th.text.strip())
        print("table header ok")
        
        # Récupération des données
        current_date_data = None
        tr_elements = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
        
        for tr in tr_elements:
            # Vérifier si c'est une ligne de date
            date_td = tr.find_elements(By.CSS_SELECTOR, "td.theDay")
            if date_td:
                # Nouvelle date trouvée
                current_date_data = dateTD(date=date_td[0].text.strip(), tab=[])
                data.append(current_date_data)
                print(f"Date trouvée: {date_td[0].text.strip()}")
            else:
                # C'est une ligne de données normale
                tds = tr.find_elements(By.CSS_SELECTOR, "td")
                if len(tds) >= 7 and current_date_data is not None:
                    # Extraire les données des 7 colonnes
                    time_val = tds[0].text.strip() if tds[0].text.strip() else ""
                    cur_val = tds[1].text.strip() if tds[1].text.strip() else ""
                    imp_val = tds[2].text.strip() if tds[2].text.strip() else ""
                    event_val = tds[3].text.strip() if tds[3].text.strip() else ""
                    actual_val = tds[4].text.strip() if tds[4].text.strip() else "0"
                    forecast_val = tds[5].text.strip() if tds[5].text.strip() else ""
                    previous_val = tds[6].text.strip() if tds[6].text.strip() else ""
                    
                    # Ajouter aux données
                    current_date_data.tab.append(
                        dataTH(
                            Time=time_val,
                            Cur=cur_val,
                            Imp=imp_val,
                            Event=event_val,
                            Actual=actual_val,
                            Forecast=forecast_val,
                            Previous=previous_val
                        )
                    )
        
        # Affichage des données collectées
        print(f"Nombre de jours trouvés: {len(data)}")
        for day in data:
            print(f"Date: {day.date}, Événements: {len(day.tab)}")
            for event in day.tab:
                print(f"  - {event.Time} {event.Cur}: {event.Event}, actual: {event.Actual}, forecast: {event.Forecast}, previous: {event.Previous}")
        
        print("table body ok")
        
    except TimeoutException:
        print("Erreur lors de la récupération du tableau")
    except Exception as e:
        print(f"Erreur inattendue: {e}")

except TimeoutException:
    print("Aucun filtrage trouvé")

# ===================== EXPORT VERS EXCEL AVEC SECTIONS GROUPÉES =====================

def export_sections_by_date(data: List[dateTD]):
    """Exporte les données avec sections groupées par date dans un seul onglet"""
    
    # Générer le nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"economic_calendar_sections_{timestamp}.xlsx"
    
    # Préparer toutes les lignes avec sections
    all_rows = []
    total_events = 0
    
    print("\n" + "="*60)
    print("📋 CRÉATION DES SECTIONS PAR DATE")
    print("="*60)
    
    for i, day_data in enumerate(data):
        if day_data.tab:  # Si il y a des événements pour cette date
            
            # Ajouter ligne de titre avec la date (en gras avec ===)
            date_header = f"=== {day_data.date} ==="
            all_rows.append([date_header, '', '', '', '', '', ''])
            
            print(f"📅 {day_data.date}: {len(day_data.tab)} événements")
            
            # Ajouter les événements de cette date
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
            
            # Ajouter ligne vide pour séparer les dates (sauf pour la dernière)
            if i < len(data) - 1:
                all_rows.append(['', '', '', '', '', '', ''])
    
    # Créer DataFrame avec toutes les données
    if all_rows:
        df_all = pd.DataFrame(all_rows, columns=[
            'Time', 'Currency', 'Impact', 'Event', 
            'Actual', 'Forecast', 'Previous'
        ])
        
        # Exporter vers Excel
        try:
            df_all.to_excel(filename, index=False, sheet_name='Economic Calendar')
            
            print("\n" + "="*60)
            print("✅ EXPORT TERMINÉ")
            print("="*60)
            print(f"📂 Fichier créé: {filename}")
            print(f"📊 Total événements: {total_events}")
            print(f"📅 Nombre de dates: {len([d for d in data if d.tab])}")
            print(f"📋 Lignes totales (avec sections): {len(df_all)}")
            
            # Aperçu de la structure
            print(f"\n📋 APERÇU DE LA STRUCTURE:")
            print("-" * 40)
            section_count = len([row for row in all_rows if row[0].startswith('===')])
            empty_count = len([row for row in all_rows if all(cell == '' for cell in row)])
            data_count = len(all_rows) - section_count - empty_count
            
            print(f"• Sections de dates: {section_count}")
            print(f"• Lignes de données: {data_count}")
            print(f"• Lignes de séparation: {empty_count}")
            
            # Afficher les premières lignes comme exemple
            print(f"\n📋 EXEMPLE DES PREMIÈRES LIGNES:")
            print("-" * 40)
            for i, row in enumerate(all_rows[:10]):
                if row[0].startswith('==='):
                    print(f"📅 {row[0]}")
                elif all(cell == '' for cell in row):
                    print("   (ligne vide)")
                else:
                    print(f"   {row[0]} | {row[1]} | {row[2]} | {row[3][:30]}...")
                    
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'export Excel: {e}")
            return False
    else:
        print("❌ Aucune donnée à exporter")
        return False

# Lancer l'export
if data:
    export_sections_by_date(data)
else:
    print("❌ Aucune donnée collectée pour l'export")

time.sleep(2)
driver.quit()