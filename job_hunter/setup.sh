#!/bin/bash
# Installation et lancement du chasseur d'emplois TI - Rouyn-Noranda

set -e

echo "=== Installation du Chasseur d'Emplois TI ==="

# Vérifie Python 3.9+
python3 --version || { echo "Python 3.9+ requis"; exit 1; }

# Crée un environnement virtuel
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Environnement virtuel créé."
fi

source venv/bin/activate

# Installe les dépendances
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Installe Playwright et les navigateurs
python -m playwright install chromium
python -m playwright install-deps chromium 2>/dev/null || true

echo ""
echo "=== Configuration ==="
echo "Ajoute ta clé API Anthropic:"
echo "  export ANTHROPIC_API_KEY='ta-clé-ici'"
echo ""
echo "Puis lance:"
echo "  python main.py           # Mode complet (scrape + évalue + postule)"
echo "  python main.py --visible # Avec navigateur visible"
echo "  python main.py --scrape-only  # Sans postulation"
echo "  python main.py --apply-only   # Postule aux offres déjà trouvées"
echo "  python main.py --report-only  # Génère le rapport HTML"
