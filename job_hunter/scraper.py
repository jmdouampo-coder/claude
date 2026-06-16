"""
Scraping des offres d'emploi TI - Rouyn-Noranda
Sources: Indeed, Jobillico, Jobboom, Emploi Québec, sites locaux, mines Abitibi
"""

import requests
import time
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from config import CANDIDATE_PROFILE, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX
from database import save_job, already_seen

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-CA,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def delay():
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))


def get_page(url, params=None):
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  [ERREUR] {url}: {e}")
        return None


def scrape_indeed():
    """Scrape Indeed Canada pour Rouyn-Noranda"""
    print("\n[Indeed] Recherche en cours...")
    jobs = []
    keywords = "technicien informatique OR analyste données OR support TI OR IT"

    for page in range(0, 3):  # 3 pages = ~45 offres
        url = "https://ca.indeed.com/jobs"
        params = {
            "q": keywords,
            "l": "Rouyn-Noranda, QC",
            "radius": "50",
            "start": page * 15,
            "lang": "fr",
        }

        soup = get_page(url, params=params)
        if not soup:
            break

        cards = soup.find_all("div", class_=lambda c: c and "job_seen_beacon" in c)
        if not cards:
            # Essaie un autre sélecteur
            cards = soup.find_all("div", attrs={"data-testid": "slider_item"})

        print(f"  Page {page+1}: {len(cards)} offres trouvées")

        for card in cards:
            try:
                title_el = card.find("h2", class_=lambda c: c and "jobTitle" in c)
                title = title_el.get_text(strip=True) if title_el else ""

                company_el = card.find("span", {"data-testid": "company-name"})
                company = company_el.get_text(strip=True) if company_el else ""

                location_el = card.find("div", {"data-testid": "text-location"})
                location = location_el.get_text(strip=True) if location_el else ""

                salary_el = card.find("div", class_=lambda c: c and "salary" in str(c).lower())
                salary = salary_el.get_text(strip=True) if salary_el else ""

                link_el = card.find("a", href=True)
                if link_el:
                    href = link_el["href"]
                    job_url = urljoin("https://ca.indeed.com", href)
                else:
                    continue

                if not title or already_seen(job_url):
                    continue

                job_id = save_job("Indeed", title, company, location, job_url, salary=salary)
                if job_id:
                    jobs.append({
                        "id": job_id, "title": title, "company": company,
                        "location": location, "url": job_url, "salary": salary,
                        "source": "Indeed"
                    })
                    print(f"  + {title} @ {company} ({location})")

            except Exception as e:
                continue

        delay()

    return jobs


def scrape_jobillico():
    """Scrape Jobillico pour Rouyn-Noranda"""
    print("\n[Jobillico] Recherche en cours...")
    jobs = []

    for keyword in ["informatique", "technicien TI", "analyste données"]:
        url = "https://www.jobillico.com/recherche-emploi"
        params = {
            "skwd": keyword,
            "scty": "Rouyn-Noranda",
        }

        soup = get_page(url, params=params)
        if not soup:
            continue

        cards = soup.find_all("article", class_=lambda c: c and "job" in str(c).lower())
        if not cards:
            cards = soup.find_all("li", class_=lambda c: c and "job" in str(c).lower())

        print(f"  '{keyword}': {len(cards)} offres")

        for card in cards:
            try:
                title_el = card.find(["h2", "h3", "h4"])
                title = title_el.get_text(strip=True) if title_el else ""

                link_el = card.find("a", href=True)
                if not link_el:
                    continue
                href = link_el["href"]
                job_url = urljoin("https://www.jobillico.com", href) if not href.startswith("http") else href

                company_el = card.find(class_=lambda c: c and "compan" in str(c).lower())
                company = company_el.get_text(strip=True) if company_el else ""

                if not title or already_seen(job_url):
                    continue

                job_id = save_job("Jobillico", title, company, "Rouyn-Noranda", job_url)
                if job_id:
                    jobs.append({
                        "id": job_id, "title": title, "company": company,
                        "location": "Rouyn-Noranda", "url": job_url,
                        "source": "Jobillico"
                    })
                    print(f"  + {title} @ {company}")

            except Exception:
                continue

        delay()

    return jobs


def scrape_jobboom():
    """Scrape Jobboom pour Rouyn-Noranda"""
    print("\n[Jobboom] Recherche en cours...")
    jobs = []

    url = "https://www.jobboom.com/fr/emploi/"
    params = {
        "q": "informatique technicien TI",
        "l": "Rouyn-Noranda, Québec",
        "d": "50",
    }

    soup = get_page(url, params=params)
    if not soup:
        return jobs

    cards = soup.find_all(class_=lambda c: c and "offer" in str(c).lower())
    print(f"  {len(cards)} offres trouvées")

    for card in cards:
        try:
            title_el = card.find(["h2", "h3"])
            title = title_el.get_text(strip=True) if title_el else ""

            link_el = card.find("a", href=True)
            if not link_el:
                continue
            href = link_el["href"]
            job_url = urljoin("https://www.jobboom.com", href) if not href.startswith("http") else href

            company_el = card.find(class_=lambda c: c and "compan" in str(c).lower())
            company = company_el.get_text(strip=True) if company_el else ""

            if not title or already_seen(job_url):
                continue

            job_id = save_job("Jobboom", title, company, "Rouyn-Noranda", job_url)
            if job_id:
                jobs.append({
                    "id": job_id, "title": title, "company": company,
                    "location": "Rouyn-Noranda", "url": job_url,
                    "source": "Jobboom"
                })
                print(f"  + {title} @ {company}")

        except Exception:
            continue

    return jobs


def fetch_job_description(url):
    """Récupère la description complète d'une offre"""
    soup = get_page(url)
    if not soup:
        return ""

    # Cherche le contenu principal
    for selector in [
        {"id": "jobDescriptionText"},
        {"class_": lambda c: c and "description" in str(c).lower()},
        {"class_": lambda c: c and "jobDetail" in str(c).lower()},
    ]:
        el = soup.find(["div", "section"], **selector)
        if el:
            return el.get_text(separator="\n", strip=True)[:3000]

    # Fallback: le body
    body = soup.find("body")
    return body.get_text(separator="\n", strip=True)[:3000] if body else ""


def scrape_emplois_gc():
    """Scrape Emplois GC (gouvernement fédéral) pour Rouyn-Noranda"""
    print("\n[Emplois GC] Recherche en cours...")
    jobs = []

    for keyword in ["technicien informatique", "analyste TI", "informatique"]:
        url = "https://emplois.gc.ca/job-emploi/jobs-emplois/search-recherche"
        params = {"searchValue": keyword, "locationValue": "Rouyn-Noranda"}

        soup = get_page(url, params=params)
        if not soup:
            continue

        cards = soup.find_all(["article", "div", "li"],
                              class_=lambda c: c and any(k in str(c).lower()
                              for k in ["job", "result", "posting"]))
        print(f"  '{keyword}': {len(cards)} résultats")

        for card in cards:
            try:
                title_el = card.find(["h2", "h3", "a"])
                title = title_el.get_text(strip=True) if title_el else ""
                link_el = card.find("a", href=True)
                if not link_el or not title:
                    continue
                href = link_el["href"]
                job_url = urljoin("https://emplois.gc.ca", href)
                if already_seen(job_url):
                    continue
                job_id = save_job("Emplois GC", title, "Gouvernement du Canada",
                                  "Rouyn-Noranda", job_url)
                if job_id:
                    jobs.append({"id": job_id, "title": title, "company": "Gouvernement du Canada",
                                 "location": "Rouyn-Noranda", "url": job_url, "source": "Emplois GC"})
                    print(f"  + {title}")
            except Exception:
                continue
        delay()

    return jobs


def scrape_ville_rouyn():
    """Scrape les offres de la Ville de Rouyn-Noranda"""
    print("\n[Ville Rouyn-Noranda] Recherche en cours...")
    jobs = []

    url = "https://www.ville.rouyn-noranda.qc.ca/fr/emplois"
    soup = get_page(url)
    if not soup:
        return jobs

    # Offres listées sur la page emplois municipaux
    cards = soup.find_all(["article", "div", "li", "tr"],
                          class_=lambda c: c and any(k in str(c).lower()
                          for k in ["emploi", "poste", "job", "offre"]))

    links = soup.find_all("a", href=lambda h: h and "emploi" in h.lower())
    print(f"  {len(cards)} cartes, {len(links)} liens emplois")

    seen_urls = set()
    for link in links:
        try:
            href = link["href"]
            job_url = urljoin("https://www.ville.rouyn-noranda.qc.ca", href)
            if job_url in seen_urls or already_seen(job_url):
                continue
            seen_urls.add(job_url)
            title = link.get_text(strip=True)
            if len(title) < 5:
                continue
            job_id = save_job("Ville Rouyn-Noranda", title, "Ville de Rouyn-Noranda",
                              "Rouyn-Noranda", job_url)
            if job_id:
                jobs.append({"id": job_id, "title": title, "company": "Ville de Rouyn-Noranda",
                             "location": "Rouyn-Noranda", "url": job_url, "source": "Ville Rouyn-Noranda"})
                print(f"  + {title}")
        except Exception:
            continue

    return jobs


def scrape_uqat():
    """Scrape les offres de l'UQAT"""
    print("\n[UQAT] Recherche en cours...")
    jobs = []

    url = "https://www.uqat.ca/universite/carrieres/"
    soup = get_page(url)
    if not soup:
        return jobs

    links = soup.find_all("a", href=True)
    for link in links:
        try:
            text = link.get_text(strip=True)
            href = link["href"]
            if len(text) < 8:
                continue
            if not any(k in text.lower() for k in ["technicien", "analyste", "informatique",
                                                    "ti ", "it ", "données", "systèmes"]):
                continue
            job_url = urljoin("https://www.uqat.ca", href)
            if already_seen(job_url):
                continue
            job_id = save_job("UQAT", text, "UQAT", "Rouyn-Noranda", job_url)
            if job_id:
                jobs.append({"id": job_id, "title": text, "company": "UQAT",
                             "location": "Rouyn-Noranda", "url": job_url, "source": "UQAT"})
                print(f"  + {text}")
        except Exception:
            continue

    return jobs


def scrape_agnico_eagle():
    """Scrape les offres TI d'Agnico Eagle (mines Abitibi)"""
    print("\n[Agnico Eagle] Recherche en cours...")
    jobs = []

    # API Workday d'Agnico Eagle
    for keyword in ["IT", "informatique", "technicien", "data", "SCADA", "système"]:
        url = "https://careers.agnicoeagle.com/job-search-results/"
        params = {"keyword": keyword, "location": "Quebec"}

        soup = get_page(url, params=params)
        if not soup:
            continue

        cards = soup.find_all(["li", "div", "article"],
                              class_=lambda c: c and any(k in str(c).lower()
                              for k in ["job", "position", "result", "poste"]))
        print(f"  '{keyword}': {len(cards)} résultats")

        for card in cards:
            try:
                title_el = card.find(["h2", "h3", "h4", "a"])
                title = title_el.get_text(strip=True) if title_el else ""
                link_el = card.find("a", href=True)
                if not link_el or not title:
                    continue
                href = link_el["href"]
                job_url = urljoin("https://careers.agnicoeagle.com", href)

                # Filtre: garde seulement les postes en Abitibi ou QC
                loc_el = card.find(class_=lambda c: c and "location" in str(c).lower())
                location = loc_el.get_text(strip=True) if loc_el else "Quebec"

                if already_seen(job_url):
                    continue
                job_id = save_job("Agnico Eagle", title, "Agnico Eagle Mines", location, job_url)
                if job_id:
                    jobs.append({"id": job_id, "title": title, "company": "Agnico Eagle Mines",
                                 "location": location, "url": job_url, "source": "Agnico Eagle"})
                    print(f"  + {title} ({location})")
            except Exception:
                continue
        delay()

    return jobs


def scrape_iamgold():
    """Scrape les offres TI d'IAMGOLD (mine Westwood, Abitibi)"""
    print("\n[IAMGOLD] Recherche en cours...")
    jobs = []

    url = "https://www.iamgold.com/careers/"
    soup = get_page(url)
    if not soup:
        return jobs

    links = soup.find_all("a", href=True)
    for link in links:
        try:
            text = link.get_text(strip=True)
            href = link["href"]
            if len(text) < 8:
                continue
            if not any(k in text.lower() for k in ["ti ", "it ", "technicien", "informatique",
                                                    "données", "systèmes", "scada", "data",
                                                    "analyste", "réseau", "network"]):
                continue
            job_url = urljoin("https://www.iamgold.com", href) if not href.startswith("http") else href
            if already_seen(job_url):
                continue
            job_id = save_job("IAMGOLD", text, "IAMGOLD", "Abitibi-Témiscamingue", job_url)
            if job_id:
                jobs.append({"id": job_id, "title": text, "company": "IAMGOLD",
                             "location": "Abitibi-Témiscamingue", "url": job_url, "source": "IAMGOLD"})
                print(f"  + {text}")
        except Exception:
            continue

    return jobs


def scrape_linkedin_mining():
    """Scrape LinkedIn pour postes TI + mines région Abitibi"""
    print("\n[LinkedIn - Mines TI] Recherche en cours...")
    jobs = []

    # LinkedIn via URL publique (sans login) - résultats limités
    for keyword in ["IT mines Quebec", "technicien informatique mine Abitibi",
                    "SCADA minier Quebec", "analyste données mines"]:
        encoded = quote_plus(keyword)
        url = f"https://www.linkedin.com/jobs/search/?keywords={encoded}&location=Abitibi-T%C3%A9miscamingue"

        soup = get_page(url)
        if not soup:
            continue

        cards = soup.find_all("div", class_=lambda c: c and "job-search-card" in str(c))
        if not cards:
            cards = soup.find_all("li", class_=lambda c: c and "jobs-search" in str(c))
        print(f"  '{keyword}': {len(cards)} résultats")

        for card in cards:
            try:
                title_el = card.find(["h3", "h4", "a"], class_=lambda c: c and "title" in str(c).lower())
                title = title_el.get_text(strip=True) if title_el else ""
                company_el = card.find(class_=lambda c: c and "company" in str(c).lower())
                company = company_el.get_text(strip=True) if company_el else ""
                link_el = card.find("a", href=True)
                if not link_el or not title:
                    continue
                job_url = link_el["href"].split("?")[0]
                if already_seen(job_url):
                    continue
                job_id = save_job("LinkedIn Mines", title, company, "Abitibi-Témiscamingue", job_url)
                if job_id:
                    jobs.append({"id": job_id, "title": title, "company": company,
                                 "location": "Abitibi-Témiscamingue", "url": job_url,
                                 "source": "LinkedIn Mines"})
                    print(f"  + {title} @ {company}")
            except Exception:
                continue
        delay()

    return jobs


def scrape_all():
    """Lance tous les scrapers et retourne toutes les offres"""
    all_jobs = []

    # ── Généralistes ──────────────────────────────────────────────────
    all_jobs.extend(scrape_indeed())
    all_jobs.extend(scrape_jobillico())
    all_jobs.extend(scrape_jobboom())

    # ── Gouvernements ─────────────────────────────────────────────────
    all_jobs.extend(scrape_emplois_gc())

    # ── Sites locaux Rouyn-Noranda ────────────────────────────────────
    all_jobs.extend(scrape_ville_rouyn())
    all_jobs.extend(scrape_uqat())

    # ── Mines Abitibi ─────────────────────────────────────────────────
    all_jobs.extend(scrape_agnico_eagle())
    all_jobs.extend(scrape_iamgold())
    all_jobs.extend(scrape_linkedin_mining())

    print(f"\n[Scraper] Total: {len(all_jobs)} nouvelles offres trouvées")
    return all_jobs
