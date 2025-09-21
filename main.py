from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
import pandas as pd

# Configuration du driver
service = Service(executable_path="chromedriver.exe")

# Dates
aujourdhui = datetime.today()
il_y_a_7_jours = aujourdhui - timedelta(days=7)
date_courante = il_y_a_7_jours

# Liste pour stocker toutes les données
data = []

for _ in range(7):
    driver = webdriver.Chrome(service=service)
    
    # Construire l'URL dynamique
    url_date = date_courante.strftime("%b").lower() + str(int(date_courante.strftime("%d"))) + "." + date_courante.strftime("%Y")
    driver.get("https://www.forexfactory.com/calendar?day=" + url_date)
    time.sleep(10)  # attendre que la page charge
    
    # Récupérer le tbody
    tbody = driver.find_element(By.TAG_NAME, "tbody")
    trBody = tbody.find_elements(By.TAG_NAME, "tr")
    
    for tr in trBody:
        tds = tr.find_elements(By.TAG_NAME, "td")
        if len(tds) < 10:
            continue  # ignorer les lignes vides ou incomplètes
        
        # Extraire uniquement les colonnes voulues
        if len(tds) > 10:
            ligne = {
                "Date": date_courante.strftime("%b.%d.%Y"),
                "Heure": tds[1].text.strip(),
                "Currency": tds[3].text.strip(),
                "Impact": tds[5].text.strip(),
                "Actual": tds[7].text.strip(),
                "Forecast": tds[8].text.strip(),
                "Previous": tds[9].text.strip()
            }
        else:
            ligne = {
                "Date": "",
                "Heure": tds[0].text.strip(),
                "Currency": tds[2].text.strip(),
                "Impact": tds[4].text.strip(),
                "Actual": tds[6].text.strip(),
                "Forecast": tds[7].text.strip(),
                "Previous": tds[8].text.strip()
            }
        data.append(ligne)
    
    driver.quit()
    date_courante += timedelta(days=1)

# Exporter vers Excel
df = pd.DataFrame(data)
df.to_excel("forex_data.xlsx", index=False)
print("Export terminé !")
