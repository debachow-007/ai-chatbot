from vertexai.generative_models import GenerativeModel

_intent_model = GenerativeModel("gemini-2.0-flash")


def detect_intent(message: str) -> str:
    prompt = f"""
Classify the user's intent into one of:

portfolio, services_info, pricing, process, marketing, contact, faq, other

Return ONLY the label, no explanation.

User message: "{message}"
"""
    try:
        res = _intent_model.generate_content(prompt)
        label = res.text.strip().lower()
        # basic safety
        allowed = {
            "portfolio",
            "services_info",
            "pricing",
            "process",
            "marketing",
            "contact",
            "faq",
            "other",
        }
        return label if label in allowed else "other"
    except Exception as e:
        print("Intent error:", e)
        return "other"
