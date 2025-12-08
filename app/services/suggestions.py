from typing import List
from vertexai.generative_models import GenerativeModel

_suggest_model = GenerativeModel("gemini-2.5-flash")


def generate_suggested_questions(
    user_message: str,
    last_answer: str,
    intent: str,
) -> List[str]:
    prompt = f"""
You are helping a website chatbot for a creative agency.

User message:
{user_message}

Assistant answer:
{last_answer}

Detected intent: {intent}

Suggest 3 SHORT follow-up questions from user's point of view that:
- keep the conversation moving
- increase chances of the user asking about services or portfolio
- are friendly and natural

Return them as plain text from the user's point of view, each on a new line, no bullets, no numbering.
"""

    try:
        res = _suggest_model.generate_content(prompt)
        lines = [l.strip() for l in res.text.split("\n") if l.strip()]
        # take top 3
        return lines[:3] if lines else [
            "Can you show some of your work?",
            "What services would you recommend for my brand?",
            "How do we get started with a project?",
        ]
    except Exception as e:
        print("Suggestions error:", e)
        return [
            "Can you show some of your work?",
            "What services would you recommend for my brand?",
            "How do we get started with a project?",
        ]
