import glob
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
import requests
import os
from dataclasses import dataclass
from typing import List
from datetime import datetime
import base64

@dataclass
class DocumentData:
    title: str
    date: str
    pdf_url: str
    filename: str

# === Configuration du répertoire de téléchargement ===
base_path = r"C:\Users\Afa-tech\Desktop\disque_dur\EMIT\code\valt\front\valy\public"
download_folder = os.path.join(base_path, "ecb_documents")
os.makedirs(download_folder, exist_ok=True)

# === Configuration de Chrome ===
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

# === Préférences de téléchargement ===
prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(executable_path="chromedriver.exe")

max_retries = 3
retry_delay = 5
documents: List[DocumentData] = []
driver = None

# === Fonction utilitaire ===
def get_last_downloaded_file(download_dir):
    """Retourne le fichier le plus récemment téléchargé dans le dossier."""
    files = glob.glob(os.path.join(download_dir, '*'))
    if not files:
        return None
    return max(files, key=os.path.getctime)

try:
    # Tentatives de connexion
    for attempt in range(max_retries):
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(400)
            driver.get("https://www.ecb.europa.eu/press/pubbydate/html/index.en.html?year=2025")
            print(" Page chargée avec succès")
            break
        except (TimeoutException, WebDriverException) as e:
            print(f"Tentative {attempt + 1} échouée : {e}")
            if driver:
                driver.quit()
            time.sleep(retry_delay)
    else:
        raise Exception("Échec du chargement après plusieurs tentatives")

    wait = WebDriverWait(driver, 20)

    # Fermer un éventuel popup
    try:
        close_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".ecb-close-button, .modal-close, button[aria-label='Close']")))
        close_button.click()
        print("Popup fermé")
        time.sleep(1)
    except:
        print("Pas de popup à fermer")

    # Récupération des liens de documents
    print("\n Recherche des documents...")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".title > a")))
    document_links = driver.find_elements(By.CSS_SELECTOR, ".title > a")

    print(f" Trouvé {len(document_links)} documents")
    max_docs = min(10, len(document_links))
    print(f"\n Téléchargement des {max_docs} premiers documents...\n")

    main_page_url = driver.current_url

    for i in range(max_docs):
        try:
            document_links = driver.find_elements(By.CSS_SELECTOR, ".title > a")
            link = document_links[i]
            title = link.text.strip()
            print(f"[{i+1}/{max_docs}] Traitement : {title[:60]}...")

            driver.execute_script("arguments[0].click();", link)
            time.sleep(3)

            pdf_link = None
            wait_short = WebDriverWait(driver, 10)

            try:
                social_links = wait_short.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#ecb-social-sharing .-links"))
                )

                try:
                    pdf_element = social_links.find_element(By.CSS_SELECTOR, ".-pdf > a")
                    pdf_link = pdf_element.get_attribute('href')
                except:
                    pass

                if not pdf_link:
                    try:
                        print_element = social_links.find_element(By.CSS_SELECTOR, ".-print > a")
                        pdf_link = print_element.get_attribute('href')
                    except:
                        pass
            except:
                print("   Conteneur de partage non trouvé")

            if not pdf_link:
                all_pdf_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
                if all_pdf_links:
                    pdf_link = all_pdf_links[0].get_attribute('href')

            # Cas javascript:window.print()
            if pdf_link and 'javascript:' in pdf_link.lower():
                print("   Lien JavaScript détecté, impression PDF...")
                filename = f"{i+1}.pdf"
                filepath = os.path.join(download_folder, filename)

                try:
                    result = driver.execute_cdp_cmd("Page.printToPDF", {
                        'landscape': False,
                        'displayHeaderFooter': False,
                        'printBackground': True,
                        'preferCSSPageSize': True
                    })
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(result['data']))

                    documents.append(DocumentData(
                        title=title,
                        date=datetime.now().strftime("%Y-%m-%d"),
                        pdf_url=driver.current_url,
                        filename=filename
                    ))
                    print(f"   Téléchargé (impression): {filename}")

                except Exception as e:
                    print(f"   Erreur impression PDF: {e}")

            elif pdf_link:
                print(f"  URL PDF trouvée: {pdf_link[:80]}...")
                filename = f"{i+1}.pdf"
                filepath = os.path.join(download_folder, filename)

                # Télécharger manuellement avec requests
                response = requests.get(pdf_link, timeout=30)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                documents.append(DocumentData(
                    title=title,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    pdf_url=pdf_link,
                    filename=filename
                ))

                print(f"   Téléchargé: {filename}")
            else:
                print("   Aucun lien PDF trouvé")

            # Revenir à la page principale
            driver.get(main_page_url)
            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"   Erreur lors du traitement du document: {e}")
            try:
                driver.get(main_page_url)
                time.sleep(2)
            except:
                pass

except Exception as e:
    print(f" Erreur globale : {e}")
    import traceback
    traceback.print_exc()
finally:
    if driver:
        driver.quit()
        print("\n Navigateur fermé")

# === Résumé ===
print(f"\n{'='*70}")
print(f" RÉSUMÉ DU TÉLÉCHARGEMENT")
print(f"{'='*70}")
print(f"PDFs téléchargés : {len(documents)}/{max_docs if 'max_docs' in locals() else 0}")
print(f"Dossier : {download_folder}")
print(f"{'='*70}")

if documents:
    print("\n Fichiers téléchargés :")
    for doc in documents:
        print(f"  - {doc.filename}")

print("\n Processus terminé avec succès !")

sys.exit(0 if documents else 1)
