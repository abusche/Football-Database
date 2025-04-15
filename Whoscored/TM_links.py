from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time

def get_link_current_month(url):

    options = Options()
    options.add_argument("--headless")  # Mode headless activé
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    all_links = []

    try:
        driver.get(url)
        
        # Accepter les cookies si la bannière apparaît
        try:
            accept_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "qc-cmp-cleanslate"))
            )
            driver.execute_script("arguments[0].click();", accept_cookies)
            time.sleep(2)
        except Exception:
            print("Bannière de cookies non détectée.")
        
        time.sleep(2)  # Attendre le chargement de la page
        
        # Récupération du HTML
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # Extraction des liens
        code = soup.find_all("div", class_="Match-module_right_oddsOn__o-ux-")
        for c in code:
            if c.find("a") is not None:
                all_links.append("https://fr.whoscored.com" + c.find("a").get("href"))
            
    except Exception as e:
        print(e)
    finally:
        driver.quit()

    return all_links
