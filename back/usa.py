import glob
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
import requests
import os
from dataclasses import dataclass
from typing import List
from datetime import datetime
import base64
from webdriver_manager.chrome import ChromeDriverManager
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

@dataclass
class DocumentData:
    title: str
    date: str
    pdf_url: str
    filename: str

def clean_filename(title: str, max_length: int = 100) -> str:
    """Convertit un titre en nom de fichier valide."""
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    filename = re.sub(r'\s+', ' ', filename)
    filename = filename.replace(' ', '_')
    filename = filename.replace('.', '_')
    if len(filename) > max_length:
        filename = filename[:max_length]
    filename = filename.strip('_')
    return filename

# === Configuration ===
base_path = r"C:\Users\Afa-tech\Desktop\disque_dur\EMIT\code\valt\front\valy\public"
download_folder = os.path.join(base_path, "usa_documents")
os.makedirs(download_folder, exist_ok=True)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
documents: List[DocumentData] = []
driver = None

try:
    # Connexion
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(400)
    driver.get("https://www.federalreserve.gov/newsevents/pressreleases.htm")
    print("✓ Page chargée avec succès")
    
    wait = WebDriverWait(driver, 20)

    # Fermer popup éventuel
    try:
        close_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".ecb-close-button, .modal-close, button[aria-label='Close']")))
        close_button.click()
        print("✓ Popup fermé")
        time.sleep(1)
    except:
        print("✓ Pas de popup")

    # Récupération des liens
    print("\n📄 Recherche des documents...")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".itemTitle > a")))
    document_links = driver.find_elements(By.CSS_SELECTOR, ".itemTitle > a")

    print(f"✓ Trouvé {len(document_links)} documents")
    max_docs = min(10, len(document_links))
    
    # Extraire toutes les infos AVANT de commencer
    links_data = []
    for link in document_links[:max_docs]:
        links_data.append({
            'title': link.text.strip(),
            'href': link.get_attribute('href')
        })
    
    print(f"\n📥 Téléchargement des {max_docs} premiers documents...\n")

    for i, link_data in enumerate(links_data):
        try:
            title = link_data['title']
            link_href = link_data['href']
            print(f"[{i+1}/{max_docs}] Traitement : {title[:60]}...")
            print(f"   🔗 URL: {link_href}")

            filename = f"{i+1}.pdf"
            filepath = os.path.join(download_folder, filename)
            pdf_link = None

            # Vérifier si c'est un PDF direct
            if link_href and link_href.lower().endswith('.pdf'):
                print("   📎 Lien PDF direct détecté")
                pdf_link = link_href
                
                try:
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
                    print(f"   ✓ Téléchargé (direct): {filename}")
                except Exception as e:
                    print(f"   ✗ Erreur téléchargement direct: {e}")
                
                time.sleep(random.uniform(0.5, 1))
                continue
            
            # Sinon, naviguer vers la page
            driver.get(link_href)
            time.sleep(2)

            # Chercher le PDF sur la page
            try:
                # Méthode 1 : Chercher tous les liens se terminant par .pdf
                pdf_elements = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
                
                if pdf_elements:
                    # Prioriser les liens dans le dossier /files/
                    for elem in pdf_elements:
                        href = elem.get_attribute('href')
                        if href and '/files/' in href:
                            pdf_link = href
                            print(f"   ✓ PDF trouvé dans /files/: {pdf_link.split('/')[-1]}")
                            break
                    
                    # Si pas trouvé dans /files/, prendre le premier PDF
                    if not pdf_link and pdf_elements:
                        pdf_link = pdf_elements[0].get_attribute('href')
                        print(f"   ✓ PDF trouvé: {pdf_link.split('/')[-1]}") # type: ignore
                
                # Méthode 2 : Chercher via XPath pour les liens contenant "(PDF)"
                if not pdf_link:
                    xpath_queries = [
                        "//a[contains(text(), '(PDF)')]",
                        "//a[contains(., 'PDF')]",
                        "//a[contains(@href, '.pdf')]"
                    ]
                    
                    for xpath in xpath_queries:
                        try:
                            elements = driver.find_elements(By.XPATH, xpath)
                            if elements:
                                pdf_link = elements[0].get_attribute('href')
                                print(f"   ✓ PDF trouvé via XPath: {pdf_link.split('/')[-1]}")  # type: ignore
                                break
                        except:
                            continue
                        
            except Exception as e:
                print(f"   ⚠ Erreur recherche PDF: {e}")

            if pdf_link:
                print(f"   🔗 URL PDF: {pdf_link[:80]}...")
                
                # Cas javascript:window.print()
                if 'javascript:' in pdf_link.lower():
                    print("   🖨 Lien JavaScript détecté, impression PDF...")
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
                        print(f"   ✓ Téléchargé (impression): {filename}")
                    except Exception as e:
                        print(f"   ✗ Erreur impression PDF: {e}")
                else:
                    # Télécharger avec requests
                    try:
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
                        print(f"   ✓ Téléchargé: {filename}")
                    except Exception as e:
                        print(f"   ✗ Erreur téléchargement: {e}")
            else:
                print("   ✗ Aucun lien PDF trouvé")
                # Debug: Afficher des informations sur la page
                all_links = driver.find_elements(By.TAG_NAME, "a")
                print(f"   ℹ Total de liens sur la page: {len(all_links)}")
                
                # Chercher des liens contenant 'pdf' dans l'attribut href
                pdf_hrefs = []
                for a in all_links[:50]:  # Limiter à 50 pour ne pas saturer
                    href = a.get_attribute('href')
                    if href and 'pdf' in href.lower():
                        pdf_hrefs.append(href)
                
                if pdf_hrefs:
                    print(f"   ℹ Liens contenant 'pdf' trouvés: {len(pdf_hrefs)}")
                    for idx, href in enumerate(pdf_hrefs[:3]):
                        print(f"   ℹ [{idx+1}] {href}")
                else:
                    print("   ℹ Aucun lien contenant 'pdf' dans href")
                    # Afficher quelques liens pour debug
                    print("   ℹ Premiers liens trouvés:")
                    for a in all_links[:5]:
                        href = a.get_attribute('href')
                        text = a.text.strip()[:50] if a.text else ""
                        if href:
                            print(f"      - {text}: {href[:80]}")

            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"   ✗ Erreur: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(2)

except Exception as e:
    print(f"✗ Erreur globale : {e}")
    import traceback
    traceback.print_exc()
finally:
    if driver:
        driver.quit()
        print("\n🔒 Navigateur fermé")

# === Résumé ===
print(f"\n{'='*70}")
print(f"📊 RÉSUMÉ DU TÉLÉCHARGEMENT")
print(f"{'='*70}")
print(f"PDFs téléchargés : {len(documents)}/{max_docs if 'max_docs' in locals() else 0}")
print(f"Dossier : {download_folder}")
print(f"{'='*70}")

if documents:
    print("\n📁 Fichiers téléchargés :")
    for doc in documents:
        print(f"  • {doc.filename}")
        print(f"    Titre: {doc.title[:80]}{'...' if len(doc.title) > 80 else ''}")

print("\n✅ Processus terminé avec succès !")

sys.exit(0 if documents else 1)