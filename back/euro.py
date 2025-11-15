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
import sys
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
    """
    Convertit un titre en nom de fichier valide.
    
    Args:
        title: Le titre du document
        max_length: Longueur maximale du nom (sans l'extension)
    
    Returns:
        Un nom de fichier nettoyé
    """
    # Supprimer les caractères non autorisés dans les noms de fichiers Windows
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    
    # Remplacer les espaces multiples par un seul
    filename = re.sub(r'\s+', ' ', filename)
    
    # Remplacer les espaces par des underscores
    filename = filename.replace(' ', '_')
    
    # Supprimer les points sauf le dernier (pour l'extension)
    filename = filename.replace('.', '_')
    
    # Limiter la longueur
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    # Supprimer les underscores en début/fin
    filename = filename.strip('_')
    
    return filename

# === Configuration du répertoire de téléchargement ===
base_path = r"C:\Users\Administrator\Downloads\valyfrontBack-main\valyfrontBack-main\front\valy\public"
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

service = Service(ChromeDriverManager().install())

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
            print("✓ Page chargée avec succès")
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
        print("✓ Popup fermé")
        time.sleep(1)
    except:
        print("✓ Pas de popup à fermer")

    # Récupération des liens de documents
    print("\n📄 Recherche des documents...")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".title > a")))
    document_links = driver.find_elements(By.CSS_SELECTOR, ".title > a")

    print(f"✓ Trouvé {len(document_links)} documents")
    max_docs = min(10, len(document_links))
    
    # Extraire TOUTES les infos des liens AVANT de commencer les téléchargements
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

            # Vérifier si le lien pointe directement vers un PDF
            if link_href and link_href.lower().endswith('.pdf'):
                print("   📎 Lien PDF direct détecté")
                pdf_link = link_href
                
                # Nom de fichier numéroté simple
                filename = f"{i+1}.pdf"
                filepath = os.path.join(download_folder, filename)
                
                # Télécharger le PDF directement sans naviguer
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
                
                # Pas besoin de naviguer
                time.sleep(random.uniform(0.5, 1))
                continue
            
            # Si ce n'est pas un PDF direct, naviguer vers l'URL
            driver.get(link_href)
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
                print("   ⚠ Conteneur de partage non trouvé")

            if not pdf_link:
                all_pdf_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
                if all_pdf_links:
                    pdf_link = all_pdf_links[0].get_attribute('href')

            # Nom de fichier numéroté simple
            filename = f"{i+1}.pdf"
            filepath = os.path.join(download_folder, filename)

            # Cas javascript:window.print()
            if pdf_link and 'javascript:' in pdf_link.lower():
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

            elif pdf_link:
                print(f"   🔗 URL PDF trouvée: {pdf_link[:80]}...")

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

                print(f"   ✓ Téléchargé: {filename}")
            else:
                print("   ✗ Aucun lien PDF trouvé")

            # Petite pause entre les documents
            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"   ✗ Erreur lors du traitement du document: {e}")
            # Continue avec le document suivant sans essayer de revenir
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