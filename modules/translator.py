from deep_translator import GoogleTranslator
import re

def normalize_query(query: str) -> str:
    """
    Convert Hinglish / Hindi / layman query into clean English text.
    """
    query = query.strip()

    # 1. Translate if Hindi detected
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(query)
    except Exception:
        translated = query  # fallback if API fails

    # 2. Replace common Hinglish slang to formal words
    replacements = {
        "paani": "water",
        "data dikha": "show data",
        "level": "water level",
        "dikha de": "show",
        "batade": "show",
        "info": "information",
        "groundwater": "water",
    }
    for slang, proper in replacements.items():
        translated = re.sub(rf"\b{slang}\b", proper, translated, flags=re.IGNORECASE)

    return translated
