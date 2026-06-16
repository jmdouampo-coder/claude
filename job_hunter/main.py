#!/usr/bin/env python3
"""
Chasseur d'emplois TI - Rouyn-Noranda
Usage: python main.py [--headless] [--scrape-only] [--apply-only]
"""

import argparse
import sys
from database import init_db, get_pending_jobs
from scraper import scrape_all
from evaluator import evaluate_all
from applier import apply_to_all
from report import generate_report
from config import CANDIDATE_PROFILE


def print_banner():
    print("=" * 60)
    print("  CHASSEUR D'EMPLOIS TI - ROUYN-NORANDA")
    print(f"  Candidat: {CANDIDATE_PROFILE['name']}")
    print(f"  Email: {CANDIDATE_PROFILE['email']}")
    print(f"  Score minimum: {CANDIDATE_PROFILE['min_score']:.0%}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Chasseur d'emplois TI - Rouyn-Noranda")
    parser.add_argument("--headless", action="store_true", default=True,
                        help="Mode sans interface graphique (défaut: True)")
    parser.add_argument("--visible", action="store_true",
                        help="Affiche le navigateur lors des candidatures")
    parser.add_argument("--scrape-only", action="store_true",
                        help="Scrape et évalue seulement, sans postuler")
    parser.add_argument("--apply-only", action="store_true",
                        help="Postule aux offres déjà évaluées en DB")
    parser.add_argument("--report-only", action="store_true",
                        help="Génère seulement le rapport HTML")
    args = parser.parse_args()

    headless = not args.visible

    print_banner()

    # Initialise la DB
    init_db()

    if args.report_only:
        report_path = generate_report()
        print(f"Rapport: {report_path}")
        return

    evaluated_jobs = []

    if not args.apply_only:
        # 1. Scraping
        print("\n[1/3] SCRAPING DES OFFRES...")
        new_jobs = scrape_all()

        if not new_jobs:
            print("  Aucune nouvelle offre trouvée.")
        else:
            # 2. Évaluation
            print("\n[2/3] ÉVALUATION PAR IA...")
            evaluated_jobs = evaluate_all(new_jobs)

    # 3. Postulation
    if not args.scrape_only:
        print("\n[3/3] POSTULATION AUTOMATIQUE...")

        if args.apply_only:
            # Récupère les offres en attente de la DB
            pending = get_pending_jobs(CANDIDATE_PROFILE["min_score"])
            jobs_to_apply = [
                {"id": r[0], "source": r[1], "title": r[2],
                 "company": r[3], "url": r[4], "score": r[5],
                 "verdict": "POSTULER"}
                for r in pending
            ]
            apply_to_all(jobs_to_apply, headless=headless)
        else:
            apply_to_all(evaluated_jobs, headless=headless)

    # 4. Rapport final
    print("\n[4/4] GÉNÉRATION DU RAPPORT...")
    report_path = generate_report(evaluated_jobs)

    print("\n" + "=" * 60)
    print("  TERMINÉ!")
    print(f"  Rapport: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
