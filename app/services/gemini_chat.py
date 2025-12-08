import vertexai
from vertexai.generative_models import GenerativeModel

from app.config import settings

vertexai.init(
    project=settings.PROJECT_ID,
    location=settings.LOCATION,
)

_chat_model = GenerativeModel(settings.CHAT_MODEL)


def generate_answer(
    user_message: str,
    context: str = "",
    chat_history: list[dict] | None = None,
    intent: str | None = None,
) -> str:
    chat_history = chat_history or []

    history_text = ""
    for m in chat_history:
        speaker = "User" if m["role"] == "user" else "Assistant"
        history_text += f"{speaker}: {m['content']}\n"

    intent_str = f"\nDetected intent: {intent}" if intent else ""

    prompt = f"""
You are Vibes AI — a senior digital consultant at Vibes Communications.
Your goal is to help business owners understand branding, website development,
marketing, and technology solutions, and guide them to take action.

Write answers that:
- are short, concise, 2–4 paragraphs max
- use bullet points whenever possible
- highlight outcomes and benefits, not features
- avoid generic filler text
- feel confident and expert
- end with ONE follow-up question to continue conversation
- if unclear intent: ask a clarifying question

NEVER respond with more than 1200 characters.
NEVER produce generic marketing fluff.

Use this context from the website when relevant:
{context}

Conversation so far:
{history_text}
User: {user_message}
{intent_str}
"""

    try:
        res = _chat_model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        print("Gemini chat error:", e)
        return (
            "I'm facing a small technical hiccup right now 😅 "
            "but I can still help if you rephrase or narrow down your question."
        )
