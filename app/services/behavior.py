def decide_behavior(intent: str, has_projects: bool) -> str:
    if intent == "portfolio" and has_projects:
        return "portfolio"
    if intent == "contact":
        return "contact_form"
    if intent == "pricing":
        return "cta"
    if intent == "process":
        return "timeline"
    return "text"

