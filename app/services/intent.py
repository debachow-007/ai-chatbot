from vertexai.generative_models import GenerativeModel

_intent_model = GenerativeModel("gemini-2.0-flash")

INTENT_LABELS = [
    "portfolio",
    "services_info",
    "pricing",
    "process",
    "marketing",
    "contact",
    "faq",
    "confused",
    "needs_help",
    "angry",
    "fallback",
    "other"
]

def detect_intent(message: str) -> str:
    prompt = f"""
Analyze the user's message and classify it into EXACTLY ONE of the following intents:

{", ".join(INTENT_LABELS)}

This is a business support and sales chatbot. Classification rules:
- If the user expresses confusion, frustration, or asks something unclear → "confused"
- If the user directly asks for help or support → "needs_help"
- If the message expresses anger or dissatisfaction → "angry"
- If the chatbot would normally say "I didn't understand" → "fallback"
- If asking for examples of work or project showcase → "portfolio"
- If asking about what services are available → "services_info"
- If asking about cost, quote, or price → "pricing"
- If asking about workflow, how it works, steps → "process"
- If asking about digital marketing topics → "marketing"
- If asking to contact, request call, booking, meeting → "contact"
- If casual questions about information and answers already available → "faq"
- If none apply → "other"

Respond ONLY with the label, no extra text.

User message:
\"\"\"{message}\"\"\"
"""

    try:
        res = _intent_model.generate_content(prompt)
        label = res.text.strip().lower()
        return label if label in INTENT_LABELS else "other"
    except Exception as e:
        print("Intent error:", e)
        return "other"
