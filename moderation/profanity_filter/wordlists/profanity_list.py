"""Curated wordlists for profanity, abusive terms, and civic grievance whitelists."""

# -------------------------------------------------------------------------
# Curated Severe Profanity & Abusive Language
# Covering Marathi (Devanagari), Romanized Marathi (Minglish), Hindi, English
# -------------------------------------------------------------------------

MARATHI_PROFANITY = {
    "भडव्या", "झावया", "रांड", "रांडेच्या", "गांड", "गांडू", "आईघाला", "मादरचोद",
    "बहिणचोद", "लांड्या", "चूतिया", "बोका", "चोद", "लवडा", "लवड्या", "झेव्या"
}

ROMAN_MARATHI_PROFANITY = {
    "bhadavya", "bhadwa", "zhavnya", "zhavadya", "randicha", "randecha", "gand",
    "gandu", "aighalya", "aaighalya", "madarchod", "behenchod", "bhenchod",
    "landya", "chutiya", "chutya", "lavda", "lavdya", "bhosadike", "bhosdike",
    "bhosadi", "chuda"
}

HINDI_PROFANITY = {
    "मादरचोद", "बहनचोद", "गांडू", "भोसडीके", "लौड़ा", "चूतिया", "हरामी",
    "harami", "kutta", "kaminey", "kamina", "suar", "saala", "saale", "raand"
}

ENGLISH_PROFANITY = {
    "fuck", "fucking", "fucker", "motherfucker", "bitch", "bastard", "asshole",
    "bullshit", "cunt", "dick", "pussy", "whore", "slut", "cock"
}

ALL_PROFANITY = MARATHI_PROFANITY | ROMAN_MARATHI_PROFANITY | HINDI_PROFANITY | ENGLISH_PROFANITY

# -------------------------------------------------------------------------
# Civic Grievance Whitelist (Words expressing citizen anger / municipal issues)
# MUST NEVER be blocked as profanity!
# -------------------------------------------------------------------------
CIVIC_GRIEVANCE_ALLOWLIST = {
    "कचरा", "घाण", "खड्डा", "खड्डे", "दुर्गंधी", "नाला", "ड्रेनेज", "घाणेरडा",
    "काम करत नाही", "कामचुकार", "लाच", "भ्रष्टाचार", "बोगस", "खराब", "रस्ता खराब",
    "पाणी नाही", "गढूळ पाणी", "बत्ती गुल", "अंधार", "पॉथोल", "गटार",
    "kachra", "ghan", "khadda", "khadde", "durgandhi", "drainage", "nala",
    "bogus", "kharab", "pani nahi", "pani yet nahi", "pothole", "gatar",
    "light band", "complaint", "takrar", "problem", "issue", "urgency"
}
