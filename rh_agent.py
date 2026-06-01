from langchain_groq import ChatGroq
from groq import Groq
import PyPDF2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))




# ===== 1. LECTURE CV =====

def read_pdf(filepath: str) -> str:
    """Lit un fichier PDF"""
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except:
        return None

def read_txt(filepath: str) -> str:
    """Lit un fichier texte"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return None

def read_cv(filepath: str) -> str:
    """Lit le CV selon son format"""
    if filepath.endswith(".pdf"):
        return read_pdf(filepath)
    elif filepath.endswith(".txt"):
        return read_txt(filepath)
    else:
        return None

# ===== 2. ANALYSE CV =====

def analyze_cv(cv_text: str) -> dict:
    """Analyse et extrait les informations du CV"""
    print("📊 Analyse du CV en cours...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Analyse ce CV et extrait les informations suivantes en JSON :
{{
    "nom": "nom complet",
    "email": "email",
    "telephone": "téléphone",
    "experience_annees": nombre,
    "competences": ["compétence1", "compétence2"],
    "langages_programmation": ["python", "java"],
    "formations": ["formation1"],
    "langues": ["français", "anglais"],
    "points_forts": ["point1", "point2"],
    "points_faibles": ["point1", "point2"]
}}

CV:
{cv_text}

Réponds UNIQUEMENT avec le JSON, sans texte avant ou après."""
        }]
    )

    import json
    try:
        result = response.choices[0].message.content
        result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result)
    except:
        return {"raw": response.choices[0].message.content}

# ===== 3. SCORE COMPATIBILITÉ =====

def score_compatibility(cv_text: str, job_description: str) -> dict:
    """Compare le CV avec l'offre d'emploi"""
    print("🎯 Calcul du score de compatibilité...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Compare ce CV avec cette offre d'emploi et donne:
1. Un score de compatibilité sur 100
2. Les compétences qui matchent
3. Les compétences manquantes
4. Une recommandation (Recommandé / À considérer / Non recommandé)

Réponds en JSON:
{{
    "score": 75,
    "competences_matchent": ["python", "sql"],
    "competences_manquantes": ["docker", "kubernetes"],
    "recommandation": "Recommandé",
    "justification": "Le candidat a..."
}}

CV:
{cv_text}

Offre d'emploi:
{job_description}

Réponds UNIQUEMENT avec le JSON."""
        }]
    )

    import json
    try:
        result = response.choices[0].message.content
        result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result)
    except:
        return {"raw": response.choices[0].message.content}

# ===== 4. SUGGESTIONS AMÉLIORATION =====

def suggest_improvements(cv_text: str, job_description: str) -> str:
    """Suggère des améliorations pour le CV"""
    print("💡 Génération des suggestions...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Tu es un expert RH. Donne 5 conseils concrets pour améliorer ce CV 
par rapport à cette offre d'emploi. Sois précis et actionnable.

CV: {cv_text}
Offre: {job_description}"""
        }]
    )
    return response.choices[0].message.content

# ===== 5. RAPPORT FINAL =====

def generate_report(cv_info: dict, score_info: dict, 
                   suggestions: str, candidate_name: str) -> str:
    """Génère un rapport PDF en markdown"""
    filename = f"rapport_rh_{candidate_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 📋 Rapport RH — {candidate_name}\n\n")
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

        f.write("## 👤 Informations candidat\n\n")
        f.write(f"- *Nom:* {cv_info.get('nom', 'N/A')}\n")
        f.write(f"- *Email:* {cv_info.get('email', 'N/A')}\n")
        f.write(f"- *Expérience:* {cv_info.get('experience_annees', 'N/A')} ans\n")
        f.write(f"- *Langues:* {', '.join(cv_info.get('langues', []))}\n\n")

        f.write("## 💻 Compétences techniques\n\n")
        for comp in cv_info.get('competences', []):
            f.write(f"- {comp}\n")

        f.write(f"\n## 🎯 Score de compatibilité: {score_info.get('score', 'N/A')}/100\n\n")
        f.write(f"*Recommandation:* {score_info.get('recommandation', 'N/A')}\n\n")
        f.write(f"*Justification:* {score_info.get('justification', 'N/A')}\n\n")

        f.write("## ✅ Compétences qui matchent\n\n")
        for comp in score_info.get('competences_matchent', []):
            f.write(f"- ✅ {comp}\n")

        f.write("\n## ❌ Compétences manquantes\n\n")
        for comp in score_info.get('competences_manquantes', []):
            f.write(f"- ❌ {comp}\n")

        f.write(f"\n## 💡 Suggestions d'amélioration\n\n{suggestions}\n")

    return filename

# ===== 6. AGENT PRINCIPAL =====

def rh_agent():
    print("=" * 50)
    print("👔 Assistant RH IA — Analyse de CV")
    print("=" * 50)

    # Demander le CV
    print("\n📄 Entrez le chemin de votre CV (PDF ou TXT)")
    print("Ou tapez 'demo' pour utiliser un CV exemple\n")
    cv_path = input("Chemin du CV: ").strip()

    if cv_path.lower() == "demo":
        cv_text = """
        John Doe - Développeur Python
        Email: john@email.com | Tel: +216 XX XXX XXX
        
        EXPÉRIENCE (3 ans):
        - Développeur Python chez TechCorp (2022-2024)
          * Développement d'APIs REST avec FastAPI
          * Travail avec PostgreSQL et Redis
          * Déploiement sur AWS
        
        COMPÉTENCES:
        Python, FastAPI, PostgreSQL, Git, Docker, SQL
        
        FORMATION:
        Licence Informatique - Université de Tunis (2021)
        
        LANGUES: Arabe (natif), Français (courant), Anglais (intermédiaire)
        """
        print("✅ CV démo chargé !")
    else:
        cv_text = read_cv(cv_path)
        if not cv_text:
            print("❌ Impossible de lire le CV")
            return

    # Demander l'offre d'emploi
    print("\n💼 Entrez l'offre d'emploi")
    print("Ou tapez 'demo' pour utiliser une offre exemple\n")
    job_input = input("Offre d'emploi: ").strip()

    if job_input.lower() == "demo":
        job_description = """
        Poste: AI Engineer
        Entreprise: TechTunis
        
        Nous cherchons un AI Engineer avec:
        - 2+ ans d'expérience en Python
        - Connaissance de LangChain ou LangGraph
        - Expérience avec les LLMs (GPT, Claude, Llama)
        - Maîtrise de Docker et Git
        - Connaissance des bases de données vectorielles
        - Anglais professionnel requis
        
        Bonus: RAG, agents IA, FastAPI
        """
        print("✅ Offre démo chargée !")
    else:
        job_description = job_input

    # Analyse complète
    print("\n🚀 Analyse en cours...\n")

    cv_info = analyze_cv(cv_text)
    score_info = score_compatibility(cv_text, job_description)
    suggestions = suggest_improvements(cv_text, job_description)

    # Afficher résultats
    candidate_name = cv_info.get('nom', 'Candidat')

    print(f"\n{'='*50}")
    print(f"📊 RÉSULTATS — {candidate_name}")
    print(f"{'='*50}")
    print(f"🎯 Score: {score_info.get('score', 'N/A')}/100")
    print(f"✅ Recommandation: {score_info.get('recommandation', 'N/A')}")
    print(f"\n✅ Compétences matchent: {', '.join(score_info.get('competences_matchent', []))}")
    print(f"❌ Compétences manquantes: {', '.join(score_info.get('competences_manquantes', []))}")
    print(f"\n💡 SUGGESTIONS:\n{suggestions}")

    # Générer rapport
    report_file = generate_report(cv_info, score_info, suggestions, candidate_name)
    print(f"\n💾 Rapport sauvegardé: {report_file}")

# ===== LANCEMENT =====
rh_agent()