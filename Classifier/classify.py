def classify_incident(text):
    text = text.lower()
    if "fire" in text:
        return "Fire"
    elif "heart" in text or "injury" in text:
        return "Medical"
    else:
        return "Police"
