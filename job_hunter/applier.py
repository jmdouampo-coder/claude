"""
Postulation automatique via Playwright
Gère Indeed, Jobillico, Jobboom et formulaires génériques
"""

import time
import random
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
from config import CANDIDATE_PROFILE
from database import save_application


EMAIL = CANDIDATE_PROFILE["email"]
NAME = CANDIDATE_PROFILE["name"]

# Lettre de motivation générique (personnalisée par poste via Claude)
COVER_LETTER_TEMPLATE = """Bonjour,

Je vous contacte pour vous soumettre ma candidature pour le poste de {title} au sein de votre organisation.

Étudiant en informatique avec des compétences en support technique et analyse de données, je suis motivé à contribuer à votre équipe dans la région de Rouyn-Noranda.

Mes compétences incluent:
- Support informatique et dépannage (Windows, Linux, réseaux)
- Analyse de données (Python, SQL, Excel, Power BI)
- Service client et communication

Je suis disponible pour un entretien à votre convenance.

Cordialement,
{name}
{email}
"""


def human_delay(min_s=0.5, max_s=1.5):
    time.sleep(random.uniform(min_s, max_s))


def fill_field(page: Page, selector: str, value: str):
    try:
        page.fill(selector, value)
        human_delay(0.3, 0.8)
    except Exception:
        pass


def apply_indeed(page: Page, job: dict) -> dict:
    """Postule sur Indeed"""
    try:
        page.goto(job["url"], wait_until="networkidle", timeout=30000)
        human_delay(1, 2)

        # Cherche le bouton "Postuler maintenant" ou "Apply now"
        apply_btn = page.locator("button:has-text('Postuler'), button:has-text('Apply'), a:has-text('Postuler')")
        if apply_btn.count() == 0:
            return {"status": "skip", "reason": "Pas de bouton postuler trouvé"}

        apply_btn.first.click()
        human_delay(2, 3)

        # Vérifie si Indeed demande de se connecter
        if "connexion" in page.url.lower() or "login" in page.url.lower() or "signin" in page.url.lower():
            return _indeed_login_or_create(page, job)

        return _fill_indeed_form(page, job)

    except PlaywrightTimeout:
        return {"status": "error", "reason": "Timeout lors du chargement"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def _indeed_login_or_create(page: Page, job: dict) -> dict:
    """Connexion ou création de compte Indeed"""
    human_delay(1, 2)

    # Tente de remplir l'email
    email_field = page.locator("input[type='email'], input[name='email']")
    if email_field.count() > 0:
        email_field.first.fill(EMAIL)
        human_delay(0.5, 1)

        # Clique sur continuer
        continue_btn = page.locator("button[type='submit'], button:has-text('Continuer'), button:has-text('Continue')")
        if continue_btn.count() > 0:
            continue_btn.first.click()
            human_delay(2, 3)

    # Note: la création de compte complète nécessite une vérification email manuelle
    return {"status": "manual_required", "reason": "Vérification email requise pour Indeed"}


def _fill_indeed_form(page: Page, job: dict) -> dict:
    """Remplit le formulaire de candidature Indeed"""
    # Cherche les champs communs
    fill_field(page, "input[name='applicant.name'], input[id*='name']", NAME)
    fill_field(page, "input[name='applicant.phoneNumber'], input[id*='phone']", "")
    fill_field(page, "textarea[id*='cover'], textarea[name*='cover']",
               COVER_LETTER_TEMPLATE.format(title=job["title"], name=NAME, email=EMAIL))

    # Soumet
    submit_btn = page.locator("button[type='submit']:has-text('Soumettre'), button:has-text('Submit')")
    if submit_btn.count() > 0:
        submit_btn.first.click()
        human_delay(2, 3)
        return {"status": "success", "reason": "Candidature soumise via Indeed"}

    return {"status": "partial", "reason": "Formulaire rempli mais soumission incertaine"}


def apply_generic(page: Page, job: dict) -> dict:
    """Postulation générique pour sites inconnus"""
    try:
        page.goto(job["url"], wait_until="networkidle", timeout=30000)
        human_delay(1, 2)

        # Cherche un formulaire de candidature
        apply_selectors = [
            "a:has-text('Postuler')", "button:has-text('Postuler')",
            "a:has-text('Apply')", "button:has-text('Apply')",
            "a:has-text('Je postule')", "a:has-text('Candidater')",
            "[class*='apply']", "[id*='apply']",
        ]

        for sel in apply_selectors:
            btn = page.locator(sel)
            if btn.count() > 0:
                btn.first.click()
                human_delay(1.5, 2.5)
                break

        # Remplit email si trouvé
        email_fields = page.locator("input[type='email']")
        if email_fields.count() > 0:
            email_fields.first.fill(EMAIL)
            human_delay(0.3, 0.7)

        # Remplit nom
        name_fields = page.locator("input[name*='name'], input[id*='name'], input[placeholder*='nom']")
        if name_fields.count() > 0:
            name_fields.first.fill(NAME)
            human_delay(0.3, 0.7)

        # Message/lettre de motivation
        text_areas = page.locator("textarea")
        if text_areas.count() > 0:
            text_areas.first.fill(
                COVER_LETTER_TEMPLATE.format(title=job["title"], name=NAME, email=EMAIL)
            )
            human_delay(0.5, 1)

        # Soumet si possible
        submit = page.locator("button[type='submit'], input[type='submit']")
        if submit.count() > 0:
            submit.first.click()
            human_delay(2, 3)
            return {"status": "success", "reason": "Formulaire générique soumis"}

        return {"status": "partial", "reason": "Champs remplis, soumission manuelle nécessaire"}

    except Exception as e:
        return {"status": "error", "reason": str(e)}


def apply_workday(page: Page, job: dict) -> dict:
    """Postulation via portail Workday (Agnico Eagle, grandes mines)"""
    try:
        page.goto(job["url"], wait_until="networkidle", timeout=30000)
        human_delay(2, 3)

        # Bouton Apply sur Workday
        apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply'), "
                                 "button:has-text('Postuler'), a:has-text('Postuler')")
        if apply_btn.count() == 0:
            return {"status": "skip", "reason": "Pas de bouton Workday trouvé"}

        apply_btn.first.click()
        human_delay(2, 3)

        # Workday demande souvent un compte — tente email
        email_field = page.locator("input[type='email'], input[autocomplete='email']")
        if email_field.count() > 0:
            email_field.first.fill(EMAIL)
            human_delay(0.5, 1)
            submit = page.locator("button[type='submit']")
            if submit.count() > 0:
                submit.first.click()
                human_delay(2, 3)

        return {"status": "manual_required",
                "reason": "Workday: vérification email requise, candidature initiée"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def apply_by_email(page: Page, job: dict) -> dict:
    """Certains sites locaux demandent juste un email de candidature"""
    try:
        page.goto(job["url"], wait_until="networkidle", timeout=30000)
        human_delay(1, 2)

        # Cherche un mailto: ou formulaire email simple
        mailto = page.locator("a[href^='mailto:']")
        if mailto.count() > 0:
            email_dest = mailto.first.get_attribute("href").replace("mailto:", "").split("?")[0]
            return {
                "status": "manual_required",
                "reason": f"Candidature par email à: {email_dest} — envoie ton CV manuellement"
            }

        return apply_generic(page, job)
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def apply_to_job(job: dict, browser_page: Page) -> dict:
    """Route vers le bon applier selon la source"""
    source = job.get("source", "").lower()
    url = job.get("url", "")

    if "indeed" in source or "indeed.com" in url:
        result = apply_indeed(browser_page, job)
    elif "agnico" in source or "workday" in url:
        result = apply_workday(browser_page, job)
    elif any(s in source for s in ["ville rouyn", "uqat", "cssat", "mrc", "emplois gc"]):
        result = apply_by_email(browser_page, job)
    else:
        result = apply_generic(browser_page, job)

    # Sauvegarde dans la DB
    save_application(
        job_db_id=job["id"],
        method=source,
        account_created=False,
        confirmation=result.get("reason", ""),
        error="" if result["status"] == "success" else result.get("reason", ""),
        status=result["status"]
    )

    return result


def apply_to_all(jobs: list, headless: bool = False):
    """Lance Playwright et postule à toutes les offres qualifiées"""
    good_jobs = [j for j in jobs if j.get("score", 0) >= CANDIDATE_PROFILE["min_score"]
                 and j.get("verdict") == "POSTULER"]

    if not good_jobs:
        print("\n[Postulation] Aucune offre ne dépasse le score minimum. Rien à postuler.")
        return

    print(f"\n[Postulation] {len(good_jobs)} offres qualifiées à traiter...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=100)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="fr-CA",
        )
        page = context.new_page()

        results = {"success": 0, "error": 0, "manual": 0}

        for i, job in enumerate(good_jobs, 1):
            print(f"\n[{i}/{len(good_jobs)}] {job['title']} @ {job.get('company', '?')}")
            print(f"  Score: {job['score']:.2f} | {job['url']}")

            result = apply_to_job(job, page)
            print(f"  Résultat: {result['status']} - {result['reason']}")

            if result["status"] == "success":
                results["success"] += 1
            elif result["status"] in ("manual_required", "partial"):
                results["manual"] += 1
            else:
                results["error"] += 1

            time.sleep(random.uniform(3, 6))  # Pause entre candidatures

        browser.close()

    print(f"\n[Postulation] Terminé!")
    print(f"  Succès: {results['success']}")
    print(f"  Manuel requis: {results['manual']}")
    print(f"  Erreurs: {results['error']}")
