# app/services/ai_service.py
import os, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # charge le fichier .env automatiquement

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Tu es un Coach Agile expert certifié Scrum.
Tu réponds UNIQUEMENT en JSON valide, sans texte avant ni après, sans balises markdown.
Pour les story points, tu utilises uniquement la suite Fibonacci : 1, 2, 3, 5, 8, 13.
1=trivial, 2=simple, 3=moyen, 5=complexe, 8=très complexe, 13=à découper."""


def analyze_ticket(title: str, description: str) -> dict:
    """
    Analyse un ticket et retourne les critères d'acceptation,
    les story points et la priorité suggérée par l'IA.
    """
    prompt = f"""Analyse ce ticket Agile et retourne UNIQUEMENT ce JSON :
{{
  "acceptance_criteria": ["critère 1", "critère 2", "critère 3"],
  "story_points": 3,
  "ai_priority_hint": "normal",
  "reasoning": "une phrase d'explication"
}}

Règles :
- acceptance_criteria : entre 3 et 6 critères
- story_points : OBLIGATOIREMENT l'un de ces chiffres : 1, 2, 3, 5, 8, 13
- ai_priority_hint : OBLIGATOIREMENT "urgent", "blocking" ou "normal"

Titre du ticket : {title}
Description : {description or "Non renseignée"}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # moins cher que gpt-4o, largement suffisant
        temperature=0.3,  # 0 = déterministe, 1 = créatif
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )

    # response.choices[0].message.content contient le texte retourné par l'IA
    raw_text = response.choices[0].message.content
    return json.loads(raw_text)


def predict_sprint_velocity(tickets: list) -> dict:
    """
    Prédit la vélocité d'un sprint à partir de la liste des tickets.
    tickets = [{"title": "...", "story_points": 5, "status": "To Do"}, ...]
    """
    prompt = f"""Voici les tickets d'un sprint :
{json.dumps(tickets, ensure_ascii=False, indent=2)}

Retourne UNIQUEMENT ce JSON :
{{
  "estimated_days": 8,
  "confidence": "medium",
  "total_points": 21,
  "risks": ["risque 1", "risque 2"],
  "recommendation": "conseil pour le Scrum Master"
}}

- confidence : "low", "medium" ou "high"
- estimated_days : nombre entier de jours ouvrés
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )

    return json.loads(response.choices[0].message.content)
