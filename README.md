# 👔 Assistant RH IA — Analyse de CVs

Agent IA qui analyse des CVs, calcule un score de compatibilité avec une offre d'emploi et génère des rapports RH.

## 🚀 Technologies
- Python
- Groq (Llama 3.3)
- PyPDF2 (lecture PDF)
- python-dotenv

## ✨ Fonctionnalités
- Lecture de CVs (PDF ou TXT)
- Extraction automatique des informations
- Score de compatibilité avec l'offre d'emploi
- Suggestions d'amélioration du CV
- Génération de rapport Markdown

## 📦 Installation
pip install groq pypdf2 python-dotenv

## ⚙️ Configuration
Crée un fichier .env :
GROQ_API_KEY=ta_clé_groq_ici

## ▶️ Utilisation
python rh_agent.py

Tape 'demo' pour tester avec un CV et une offre d'emploi exemple.
