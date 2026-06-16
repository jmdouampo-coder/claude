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

    # Mots-clés pour filtrer les offres
    "job_keywords": [
        "technicien informatique", "support TI", "analyste données",
        "analyste TI", "développeur", "informatique", "TI", "IT",
        "data analyst", "help desk", "technicien réseau",
        "agent support", "technicien système", "cloud",
    ],

    # Salaire minimum acceptable ($/heure ou $/an)
    "min_salary_hourly": 18,
    "min_score": 0.5,  # Score minimum pour postuler (0-1)
}

# Sources de recherche d'emploi
JOB_SOURCES = [
    {
        "name": "Indeed Canada",
        "base_url": "https://ca.indeed.com",
        "search_url": "https://ca.indeed.com/jobs?q={keywords}&l=Rouyn-Noranda%2C+QC&radius=50",
    },
    {
        "name": "Emploi Québec",
        "base_url": "https://placement.emploiquebec.gouv.qc.ca",
        "search_url": "https://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/richtxtoffr.asp?CL=french&CS=0",
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
]

# Base de données SQLite
DB_PATH = "job_hunter.db"

# Claude API (utilise la variable d'environnement ANTHROPIC_API_KEY)
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # Rapide et économique pour l'évaluation

# Délais entre les actions (secondes) pour éviter le blocage
REQUEST_DELAY_MIN = 2
REQUEST_DELAY_MAX = 5
