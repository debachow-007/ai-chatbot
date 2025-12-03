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
You are Vibes AI — a confident, friendly sales assistant for a creative agency.

You help users with:
- Branding
- Digital / social media marketing
- Website & app design/development
- Tech + performance marketing

Use this context from the website when relevant:
{context}

Conversation so far:
{history_text}
User: {user_message}
{intent_str}

Guidelines:
- Be concise (3–6 sentences) unless asked for more.
- Always be positively sales-oriented and invite next steps.
- If the user looks serious (portfolio, pricing, project), gently nudge to contact/quote.
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
