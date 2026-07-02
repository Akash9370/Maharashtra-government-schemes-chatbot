# app/categories.py

CATEGORY_KEYWORDS = {
    "farmer": ["farmer", "farmers", "agriculture", "krishi", "kisan", "shetkari",
               "crop", "irrigation", "dairy", "livestock", "fisheries"],
    "student": ["student", "students", "scholarship", "education", "college", "school",
                "hostel", "exam", "eklavya", "vidya", "shishya"],
    "health": ["health", "hospital", "medical", "treatment", "insurance", "arogya",
               "davakhana", "ayushman"],
    "welfare": ["pension", "old age", "senior citizen", "widow", "niradhar",
                "disability", "divyang", "destitute", "nivrutti"],
    "women": ["women", "woman", "girl", "mahila", "kanya", "ladki"],
    "housing": ["house", "housing", "home", "awas", "gharkul", "property"],
    "employment": ["employment", "job", "skill", "rojgar", "livelihood"],
    "loan": ["loan", "karj", "bank", "credit", "finance", "interest"],
}


def detect_category(text: str) -> str:
    """Single source of truth for category detection — used for both
    tagging schemes at index time and routing incoming questions."""
    t = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "loan":
            continue
        if any(w in t for w in keywords):
            return category
    if any(w in t for w in CATEGORY_KEYWORDS.get("loan", [])):
        return "loan"
    return "general"