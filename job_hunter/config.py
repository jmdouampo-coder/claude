"""
Configuration du chasseur d'emplois - Rouyn-Noranda TI
"""

# Profil du candidat
CANDIDATE_PROFILE = {
    "email": "jmi.douampo@gmail.com",
    "name": "JMI Douampo",
    "location": "Rouyn-Noranda, QC",
    "experience_level": "junior",  # junior (0-2 ans)

    # Compétences principales
    "skills": [
        # Support / Technicien
        "support informatique", "help desk", "dépannage", "installation",
        "maintenance informatique", "réseau", "Windows", "Linux", "macOS",
        "Active Directory", "Office 365", "ticketing", "ITIL",

        # Analyse / Données / IA
        "analyse de données", "Python", "SQL", "Excel", "Power BI",
        "machine learning", "intelligence artificielle", "statistiques",
        "visualisation de données", "ETL", "bases de données",
    ],

    # Mots-clés pour filtrer les offres (TI général + mines TI)
    "job_keywords": [
        # TI général
        "technicien informatique", "support TI", "analyste données",
        "analyste TI", "développeur", "informatique", "TI", "IT",
        "data analyst", "help desk", "technicien réseau",
        "agent support", "technicien système", "cloud",
        # Mines + TI
        "technicien TI mines", "informatique minier", "SCADA",
        "système contrôle", "automatisation", "technicien instrumentation",
        "technologie mine", "OT", "système industriel",
    ],

    # Entreprises minières majeures de la région Abitibi-Témiscamingue
    "mining_companies": [
        "Agnico Eagle", "IAMGOLD", "Eldorado Gold", "McEwen Mining",
        "Yamana Gold", "Hecla Mining", "Osisko", "Falco Resources",
        "Canadian Malartic", "Goldex", "LaRonde", "Westwood",
        "Lac Herbin", "Beaufor", "Géant Dormant",
    ],

    # Salaire minimum acceptable ($/heure ou $/an)
    "min_salary_hourly": 18,
    "min_score": 0.5,  # Score minimum pour postuler (0-1)
}

# Sources de recherche d'emploi
JOB_SOURCES = [
    # ── Généralistes nationaux ──────────────────────────────────────────
    {
        "name": "Indeed Canada",
        "base_url": "https://ca.indeed.com",
        "search_url": "https://ca.indeed.com/jobs?q={keywords}&l=Rouyn-Noranda%2C+QC&radius=50",
    },
    {
        "name": "Jobillico",
        "base_url": "https://www.jobillico.com",
        "search_url": "https://www.jobillico.com/recherche-emploi?skwd={keywords}&scty=Rouyn-Noranda",
    },
    {
        "name": "Jobboom",
        "base_url": "https://www.jobboom.com",
        "search_url": "https://www.jobboom.com/fr/emploi/?q={keywords}&l=Rouyn-Noranda",
    },
    # ── Gouvernement / Emploi Québec ────────────────────────────────────
    {
        "name": "Emploi Québec",
        "base_url": "https://placement.emploiquebec.gouv.qc.ca",
        "search_url": "https://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/richtxtoffr.asp?CL=french&CS=0",
    },
    {
        "name": "Emplois GC (Fédéral)",
        "base_url": "https://emplois.gc.ca",
        "search_url": "https://emplois.gc.ca/job-emploi/jobs-emplois/search-recherche?searchValue={keywords}&locationValue=Rouyn-Noranda",
    },
    # ── Sites locaux Rouyn-Noranda / Abitibi-Témiscamingue ─────────────
    {
        "name": "Ville de Rouyn-Noranda",
        "base_url": "https://www.ville.rouyn-noranda.qc.ca",
        "search_url": "https://www.ville.rouyn-noranda.qc.ca/fr/emplois",
    },
    {
        "name": "UQAT (Université du Québec en Abitibi-Témiscamingue)",
        "base_url": "https://www.uqat.ca",
        "search_url": "https://www.uqat.ca/universite/carrieres/",
    },
    {
        "name": "CSSAT (Centre de services scolaires)",
        "base_url": "https://www.cssat.qc.ca",
        "search_url": "https://www.cssat.qc.ca/emplois/",
    },
    {
        "name": "MRC Rouyn-Noranda",
        "base_url": "https://www.mrcrouyn-noranda.qc.ca",
        "search_url": "https://www.mrcrouyn-noranda.qc.ca/emplois/",
    },
    {
        "name": "Développement économique Abitibi-Témiscamingue",
        "base_url": "https://www.cdat.qc.ca",
        "search_url": "https://www.cdat.qc.ca/emplois/",
    },
    # ── Mines et industrie (Abitibi-Témiscamingue) ─────────────────────
    {
        "name": "Agnico Eagle Mines",
        "base_url": "https://www.agnicoeagle.com",
        "search_url": "https://careers.agnicoeagle.com/job-search-results/?keyword={keywords}&location=Rouyn-Noranda",
    },
    {
        "name": "IAMGOLD",
        "base_url": "https://www.iamgold.com",
        "search_url": "https://www.iamgold.com/careers/",
    },
    {
        "name": "McEwen Mining",
        "base_url": "https://www.mcewenmining.com",
        "search_url": "https://www.mcewenmining.com/careers/",
    },
    {
        "name": "Ressources Québec / Osisko",
        "base_url": "https://www.osisko.com",
        "search_url": "https://www.osisko.com/careers/",
    },
    {
        "name": "Mines Agnico (Goldex / LaRonde)",
        "base_url": "https://careers.agnicoeagle.com",
        "search_url": "https://careers.agnicoeagle.com/job-search-results/?location=Val-d%27Or&keyword={keywords}",
    },
    # ── LinkedIn (mines + TI région) ────────────────────────────────────
    {
        "name": "LinkedIn",
        "base_url": "https://www.linkedin.com",
        "search_url": "https://www.linkedin.com/jobs/search/?keywords={keywords}&location=Rouyn-Noranda%2C+Qu%C3%A9bec",
    },
]

# Base de données SQLite
DB_PATH = "job_hunter.db"

# Claude API (utilise la variable d'environnement ANTHROPIC_API_KEY)
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # Rapide et économique pour l'évaluation

# Délais entre les actions (secondes) pour éviter le blocage
REQUEST_DELAY_MIN = 2
REQUEST_DELAY_MAX = 5
