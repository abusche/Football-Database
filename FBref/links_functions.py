from datetime import datetime, timedelta
from tqdm import tqdm
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
import pandas as pd
from urllib.parse import urlparse


def parse_fbref_url(url):
    parts = urlparse(url).path.split("/")
    match_id = parts[3]
    slug = parts[4]
    tokens = slug.split("-")

    # identifier le mois dans le slug
    months = {
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    }
    month_idx = next(i for i, t in enumerate(tokens) if t in months)

    # équipes = tout avant la date
    teams = " ".join(tokens[:month_idx])

    # date au format YYYY-MM-DD
    date_str = " ".join(tokens[month_idx:month_idx+3])
    date = datetime.strptime(date_str, "%B %d %Y").strftime("%Y-%m-%d")

    # ligue
    league = " ".join(tokens[month_idx+3:])

    return {
        "id": match_id,
        "teams": teams,
        "date": date,
        "league": league,
        "url": url
    }


def gen_link_day(date_start, date_end):

    start_date = datetime.strptime(date_start, '%Y-%m-%d')
    end_date = datetime.strptime(date_end, '%Y-%m-%d')
    links_day = []
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        url = f"https://fbref.com/en/matches/{date_str}"
        links_day.append(url)
        current_date += timedelta(days=1)

    return links_day


def find_url(soup, leagues):
    base_link = 'https://fbref.com'
    links_by_date = []
    matchs = soup.find_all("div", class_="table_wrapper tabbed")

    for match in matchs:
        if match.find("a"):
            if match.find("a").text in leagues:
                m = match.find_all("a")
                for k in m:
                    href = k.get("href")
                    if "matches" in href and "Match Report" in k.text:
                        links_by_date.append(base_link + k.get("href"))

    return links_by_date


def close_popup(driver):
    try:
        close_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "modal-close"))
        )
        close_btn.click()
        time.sleep(1)
    except TimeoutException:
        pass


def get_match_link(date_start, date_end, leagues):

    links_date = gen_link_day(date_start, date_end)
    start_date = links_date[0]
    other_date = links_date[1:]

    links = []

    driver = uc.Chrome(version_main=145)

    time.sleep(3)

    try:
        driver.get(start_date)
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        time.sleep(10)

        links = links + find_url(soup, leagues)

        for i in tqdm(other_date):
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "a.button2.next")
                        )
                )
                next_button.click()

            except ElementClickInterceptedException:
                close_popup(driver)

                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "a.button2.next")
                        )
                )
                next_button.click()

            time.sleep(5)

            if driver.current_url == i:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                links = links + find_url(soup, leagues)
                time.sleep(7)

            else:
                print(driver.current_url)
                print(i)
                break

    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la page : {e} : {i}")
        return None

    finally:
        driver.quit()
        df = pd.DataFrame([parse_fbref_url(u) for u in links])
        return df
