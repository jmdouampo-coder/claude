"""
Génération du rapport HTML des offres trouvées et candidatures
"""

from datetime import datetime
from database import get_all_jobs


def generate_report(jobs_evaluated: list = None):
    """Génère un rapport HTML des offres et candidatures"""
    all_jobs = get_all_jobs()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rapport Emplois TI - Rouyn-Noranda</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background: #f0f4f8; margin: 0; padding: 20px; }}
  .header {{ background: linear-gradient(135deg, #1a365d, #2d6a8f); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
  .header h1 {{ margin: 0; font-size: 28px; }}
  .header p {{ margin: 5px 0 0; opacity: 0.8; }}
  .stats {{ display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }}
  .stat-card {{ background: white; padding: 20px; border-radius: 10px; flex: 1; min-width: 150px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .stat-card .number {{ font-size: 36px; font-weight: bold; color: #2d6a8f; }}
  .stat-card .label {{ color: #666; font-size: 14px; }}
  .job-card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #ccc; }}
  .job-card.excellent {{ border-left-color: #22c55e; }}
  .job-card.good {{ border-left-color: #3b82f6; }}
  .job-card.ok {{ border-left-color: #f59e0b; }}
  .job-card.low {{ border-left-color: #ef4444; }}
  .job-title {{ font-size: 18px; font-weight: bold; color: #1a365d; }}
  .job-meta {{ color: #666; font-size: 14px; margin: 5px 0; }}
  .score-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
  .score-excellent {{ background: #d1fae5; color: #065f46; }}
  .score-good {{ background: #dbeafe; color: #1e40af; }}
  .score-ok {{ background: #fef3c7; color: #92400e; }}
  .score-low {{ background: #fee2e2; color: #991b1b; }}
  .status-badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; margin-left: 10px; }}
  .status-success {{ background: #d1fae5; color: #065f46; }}
  .status-found {{ background: #e0e7ff; color: #3730a3; }}
  .status-error {{ background: #fee2e2; color: #991b1b; }}
  .job-reason {{ background: #f8fafc; padding: 10px; border-radius: 6px; font-size: 14px; margin-top: 10px; color: #374151; }}
  .job-link {{ color: #2d6a8f; text-decoration: none; font-size: 14px; }}
  .job-link:hover {{ text-decoration: underline; }}
  .section-title {{ font-size: 22px; font-weight: bold; color: #1a365d; margin: 25px 0 15px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Chasseur d'Emplois TI - Rouyn-Noranda</h1>
  <p>Rapport généré le {now} | jmi.douampo@gmail.com</p>
</div>
"""

    # Statistiques
    total = len(all_jobs)
    applied = sum(1 for j in all_jobs if j[6] in ("success", "partial"))
    good_matches = sum(1 for j in all_jobs if j[5] and j[5] >= 0.6)
    sources = len(set(j[1] for j in all_jobs))

    html += f"""
<div class="stats">
  <div class="stat-card"><div class="number">{total}</div><div class="label">Offres trouvées</div></div>
  <div class="stat-card"><div class="number">{good_matches}</div><div class="label">Bons matchs</div></div>
  <div class="stat-card"><div class="number">{applied}</div><div class="label">Candidatures envoyées</div></div>
  <div class="stat-card"><div class="number">{sources}</div><div class="label">Sources</div></div>
</div>
"""

    # Offres par catégorie
    def score_class(score):
        if not score:
            return "low", "score-low"
        if score >= 0.8:
            return "excellent", "score-excellent"
        if score >= 0.6:
            return "good", "score-good"
        if score >= 0.4:
            return "ok", "score-ok"
        return "low", "score-low"

    html += '<div class="section-title">Toutes les offres (triées par score)</div>'

    for job in all_jobs:
        db_id, source, title, company, url, score, status, applied_at, app_status = job
        card_class, badge_class = score_class(score)
        score_text = f"{score:.0%}" if score else "N/A"

        status_html = ""
        if app_status == "success":
            status_html = '<span class="status-badge status-success">✓ Postulé</span>'
        elif status == "found":
            status_html = '<span class="status-badge status-found">Trouvé</span>'

        html += f"""
<div class="job-card {card_class}">
  <div class="job-title">{title} {status_html}</div>
  <div class="job-meta">
    {company or 'Entreprise inconnue'} &bull; {source}
    &bull; <span class="score-badge {badge_class}">Score: {score_text}</span>
  </div>
  <a class="job-link" href="{url}" target="_blank">Voir l'offre →</a>
</div>
"""

    html += """
</body>
</html>"""

    report_path = "rapport_emplois.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[Rapport] Généré: {report_path}")
    return report_path
