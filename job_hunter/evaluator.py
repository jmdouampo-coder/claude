"""
Évaluation des offres d'emploi via Claude AI
Score 0.0 à 1.0 basé sur la compatibilité avec le profil TI junior
"""

import json
import anthropic
from config import CANDIDATE_PROFILE, CLAUDE_MODEL
from database import update_job_score
from scraper import fetch_job_description


def build_evaluation_prompt(job: dict, description: str) -> str:
    profile = CANDIDATE_PROFILE
    return f"""Tu es un recruteur expert. Évalue la compatibilité entre ce candidat et cette offre d'emploi.

## Profil du candidat
- Niveau: Junior TI (0-2 ans d'expérience)
- Compétences: Support informatique, help desk, dépannage, réseaux, Windows/Linux,
  Active Directory, Office 365, Python, SQL, analyse de données, Power BI, Excel
- Localisation: Rouyn-Noranda, QC

## Offre d'emploi
- Titre: {job.get('title', '')}
- Entreprise: {job.get('company', '')}
- Lieu: {job.get('location', '')}
- Description: {description[:2000] if description else 'Non disponible'}

## Instructions
Réponds UNIQUEMENT en JSON valide avec ce format exact:
{{
  "score": 0.75,
  "verdict": "POSTULER" ou "IGNORER",
  "raison": "Explication courte (2-3 phrases max)",
  "points_forts": ["point 1", "point 2"],
  "points_faibles": ["point 1"]
}}

Score:
- 0.8-1.0: Excellent match (postuler absolument)
- 0.6-0.79: Bon match (postuler)
- 0.4-0.59: Match partiel (à considérer)
- 0.0-0.39: Mauvais match (ignorer)

Critères importants:
- Localisation dans un rayon de 100km de Rouyn-Noranda
- Compétences TI correspondantes (support ou données/IA)
- Niveau junior acceptable
- Poste légitime en TI"""


def evaluate_job(job: dict) -> dict:
    """Évalue une offre et retourne le score + raison"""
    print(f"  Évaluation: {job['title']} @ {job.get('company', '?')}")

    # Récupère la description complète
    description = fetch_job_description(job["url"])

    client = anthropic.Anthropic()

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": build_evaluation_prompt(job, description)
            }]
        )

        content = message.content[0].text.strip()

        # Parse JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        score = float(result.get("score", 0))
        raison = result.get("raison", "")
        verdict = result.get("verdict", "IGNORER")

        print(f"    Score: {score:.2f} | {verdict} | {raison[:80]}...")

        # Met à jour la DB
        update_job_score(job["url"], score, f"{verdict}: {raison}")

        return {
            **job,
            "score": score,
            "verdict": verdict,
            "raison": raison,
            "description": description,
        }

    except json.JSONDecodeError as e:
        print(f"    [ERREUR JSON] {e} | Réponse: {content[:100]}")
        update_job_score(job["url"], 0.0, "Erreur d'évaluation")
        return {**job, "score": 0.0, "verdict": "IGNORER", "raison": "Erreur d'évaluation"}

    except Exception as e:
        print(f"    [ERREUR] {e}")
        update_job_score(job["url"], 0.0, f"Erreur: {e}")
        return {**job, "score": 0.0, "verdict": "IGNORER", "raison": str(e)}


def evaluate_all(jobs: list) -> list:
    """Évalue toutes les offres et retourne les meilleurs candidats"""
    print(f"\n[Évaluateur] Analyse de {len(jobs)} offres avec Claude AI...")
    evaluated = []

    for job in jobs:
        result = evaluate_job(job)
        evaluated.append(result)

    # Trie par score décroissant
    evaluated.sort(key=lambda x: x["score"], reverse=True)

    good = [j for j in evaluated if j["score"] >= 0.5]
    print(f"\n[Évaluateur] {len(good)}/{len(evaluated)} offres recommandées pour postulation")

    return evaluated
