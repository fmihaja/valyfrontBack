from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import subprocess
import sys

app = FastAPI(title="Scraper API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    timestamp: str

@app.get("/")
async def root():
    return {
        "message": "Scraper API",
        "endpoints": {
            "POST /scrape/economie": "Lance le scraping du calendrier économique",
            "POST /scrape/ecb": "Lance le scraping des documents ECB"
        }
    }

@app.post("/scrape/economie", response_model=ScrapeResponse)
async def scrape_economie():
    """
    Lance le scraping du calendrier économique
    """
    try:
        print("🚀 Démarrage du scraping économie...")
        
        # Exécuter le script scraper_economie.py
        result = subprocess.run(
            [sys.executable, "economic.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Vérifier si le script s'est terminé correctement
        if result.returncode == 0:
            print("✅ Scraping économie terminé")
            return ScrapeResponse(
                success=True,
                message="Scraping du calendrier économique terminé avec succès",
                timestamp=datetime.now().isoformat()
            )
        else:
            print(f"❌ Erreur scraping économie: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du scraping: {result.stderr}"
            )
    
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout scraping économie")
        raise HTTPException(
            status_code=408,
            detail="Le scraping a pris trop de temps (timeout)"
        )
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du scraping: {str(e)}"
        )

@app.post("/scrape/ecb", response_model=ScrapeResponse)
async def scrape_ecb():
    """
    Lance le scraping des documents ECB
    """
    try:
        print("🚀 Démarrage du scraping ECB...")
        
        # Exécuter le script scraper_ecb.py
        result = subprocess.run(
            [sys.executable, "euro.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout (plus long car téléchargement de PDFs)
        )
        
        # Vérifier si le script s'est terminé correctement
        if result.returncode == 0:
            print("✅ Scraping ECB terminé")
            return ScrapeResponse(
                success=True,
                message="Scraping des documents ECB terminé avec succès",
                timestamp=datetime.now().isoformat()
            )
        else:
            print(f"❌ Erreur scraping ECB: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du scraping: {result.stderr}"
            )
    
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout scraping ECB")
        raise HTTPException(
            status_code=408,
            detail="Le scraping a pris trop de temps (timeout)"
        )
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du scraping: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)