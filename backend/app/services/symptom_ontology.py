SYMPTOM_ONTOLOGY = {
    # 1. Neurological
    "migraine": {"category": "Neurological", "synonyms": ["migraine", "migraines"]},
    "headache": {"category": "Neurological", "synonyms": ["headache", "headaches", "head pain", "pain in my head", "head hurts"]},
    "vertigo": {"category": "Neurological", "synonyms": ["vertigo"]},
    "dizziness": {"category": "Neurological", "synonyms": ["dizziness", "dizzy", "lightheaded", "lightheadedness"]},
    "seizures": {"category": "Neurological", "synonyms": ["seizures", "seizure", "convulsions", "fit"]},
    "numbness": {"category": "Neurological", "synonyms": ["numbness", "numb"]},
    "tingling": {"category": "Neurological", "synonyms": ["tingling", "pins and needles"]},
    "tremors": {"category": "Neurological", "synonyms": ["tremors", "tremor", "shaking"]},
    "weakness": {"category": "Neurological", "synonyms": ["weakness", "weak", "loss of strength"]},
    "confusion": {"category": "Neurological", "synonyms": ["confusion", "confused", "disoriented"]},

    # 2. Cardiovascular
    "chest pain": {"category": "Cardiovascular", "synonyms": ["chest pain", "pain in chest", "chest hurts"]},
    "palpitations": {"category": "Cardiovascular", "synonyms": ["palpitations", "heart racing", "heart pounding"]},
    "fainting": {"category": "Cardiovascular", "synonyms": ["fainting", "faint", "passed out", "passing out", "syncope"]},
    "swelling": {"category": "Cardiovascular", "synonyms": ["swelling", "swollen", "edema"]},
    "irregular heartbeat": {"category": "Cardiovascular", "synonyms": ["irregular heartbeat", "skipped beat", "arrhythmia"]},

    # 3. Respiratory
    "cough": {"category": "Respiratory", "synonyms": ["cough", "coughing"]},
    "wheezing": {"category": "Respiratory", "synonyms": ["wheezing", "wheeze"]},
    "shortness of breath": {"category": "Respiratory", "synonyms": ["shortness of breath", "breathlessness", "out of breath", "trouble breathing", "hard to breathe"]},
    "sputum": {"category": "Respiratory", "synonyms": ["sputum", "phlegm", "coughing up mucus"]},
    "chest tightness": {"category": "Respiratory", "synonyms": ["chest tightness", "tight chest"]},

    # 4. Gastrointestinal
    "abdominal pain": {"category": "Gastrointestinal", "synonyms": ["abdominal pain", "abdomen pain"]},
    "stomach pain": {"category": "Gastrointestinal", "synonyms": ["stomach ache", "stomach pain", "belly pain", "stomach hurts", "tummy ache"]},
    "nausea": {"category": "Gastrointestinal", "synonyms": ["nausea", "nauseous", "feel sick to my stomach"]},
    "vomiting": {"category": "Gastrointestinal", "synonyms": ["vomiting", "vomit", "throwing up", "puking"]},
    "diarrhea": {"category": "Gastrointestinal", "synonyms": ["diarrhea", "diarrhoea", "loose stools", "the runs"]},
    "constipation": {"category": "Gastrointestinal", "synonyms": ["constipation", "constipated", "can't poop"]},
    "bloating": {"category": "Gastrointestinal", "synonyms": ["bloating", "bloated"]},
    "heartburn": {"category": "Gastrointestinal", "synonyms": ["heartburn", "acid reflux"]},
    "jaundice": {"category": "Gastrointestinal", "synonyms": ["jaundice", "yellow skin", "yellow eyes"]},

    # 5. ENT and ophthalmology
    "earache": {"category": "ENT", "synonyms": ["earache", "ear ache", "ear pain", "pain in my ear", "ears hurt"]},
    "ear discharge": {"category": "ENT", "synonyms": ["ear discharge", "fluid from ear"]},
    "hearing changes": {"category": "ENT", "synonyms": ["hearing changes", "hearing loss", "trouble hearing", "deafness"]},
    "sore throat": {"category": "ENT", "synonyms": ["sore throat", "throat pain", "throat hurts", "scratchy throat"]},
    "sinus pain": {"category": "ENT", "synonyms": ["sinus pain", "sinus pressure"]},
    "vision changes": {"category": "Ophthalmology", "synonyms": ["vision changes", "blurry vision", "blurred vision", "trouble seeing"]},
    "eye pain": {"category": "Ophthalmology", "synonyms": ["eye pain", "eyes hurt", "pain in eye"]},

    # 6. Dermatology and allergy
    "rash": {"category": "Dermatology", "synonyms": ["rash", "skin rash"]},
    "itching": {"category": "Dermatology", "synonyms": ["itching", "itchy", "itchiness"]},
    "hives": {"category": "Dermatology", "synonyms": ["hives", "welts"]},
    "acne": {"category": "Dermatology", "synonyms": ["acne", "pimples", "breakout"]},
    "skin discoloration": {"category": "Dermatology", "synonyms": ["skin discoloration", "discolored skin", "patchy skin"]},
    "hair loss": {"category": "Dermatology", "synonyms": ["hair loss", "losing hair", "bald patches"]},

    # 7. Musculoskeletal
    "back pain": {"category": "Musculoskeletal", "synonyms": ["back pain", "backache", "back hurts", "lower back pain"]},
    "neck pain": {"category": "Musculoskeletal", "synonyms": ["neck pain", "neck ache", "neck hurts", "stiff neck"]},
    "joint pain": {"category": "Musculoskeletal", "synonyms": ["joint pain", "joints hurt", "achy joints"]},
    "muscle pain": {"category": "Musculoskeletal", "synonyms": ["muscle pain", "body aches", "muscle ache", "muscles hurt"]},
    "stiffness": {"category": "Musculoskeletal", "synonyms": ["stiffness", "stiff"]},
    "cramps": {"category": "Musculoskeletal", "synonyms": ["cramps", "muscle cramps", "cramping"]},

    # 8. Urinary and renal
    "painful urination": {"category": "Urinary", "synonyms": ["painful urination", "burning when peeing", "pain when peeing", "dysuria"]},
    "urinary frequency": {"category": "Urinary", "synonyms": ["urinary frequency", "peeing a lot", "frequent urination"]},
    "urinary urgency": {"category": "Urinary", "synonyms": ["urinary urgency", "urgent need to pee"]},
    "blood in urine": {"category": "Urinary", "synonyms": ["blood in urine", "pink urine", "hematuria"]},
    "flank pain": {"category": "Urinary", "synonyms": ["flank pain", "kidney pain", "side pain"]},

    # 9. Reproductive and gynecological
    "pelvic pain": {"category": "Reproductive", "synonyms": ["pelvic pain", "pain in pelvis"]},
    "menstrual pain": {"category": "Reproductive", "synonyms": ["menstrual pain", "period cramps", "menstrual cramps"]},
    "abnormal bleeding": {"category": "Reproductive", "synonyms": ["abnormal bleeding", "spotting", "irregular bleeding"]},
    "vaginal discharge": {"category": "Reproductive", "synonyms": ["vaginal discharge", "unusual discharge"]},

    # 10. Endocrine and metabolic
    "excessive thirst": {"category": "Endocrine", "synonyms": ["excessive thirst", "always thirsty", "very thirsty", "polydipsia"]},
    "excessive hunger": {"category": "Endocrine", "synonyms": ["excessive hunger", "always hungry", "polyphagia"]},
    "heat intolerance": {"category": "Endocrine", "synonyms": ["heat intolerance", "can't stand the heat", "always hot"]},
    "cold intolerance": {"category": "Endocrine", "synonyms": ["cold intolerance", "always cold"]},
    "unexplained weight changes": {"category": "Endocrine", "synonyms": ["unexplained weight changes", "weight loss", "weight gain", "lost weight", "gained weight"]},

    # 11. General and infectious
    "fever": {"category": "General", "synonyms": ["fever", "high fever", "mild fever", "running a temperature", "high temp"]},
    "chills": {"category": "General", "synonyms": ["chills", "shivering"]},
    "fatigue": {"category": "General", "synonyms": ["fatigue", "tiredness", "exhausted", "tired", "exhaustion"]},
    "malaise": {"category": "General", "synonyms": ["malaise", "feel unwell", "feeling sick", "feel terrible"]},
    "night sweats": {"category": "General", "synonyms": ["night sweats", "sweating at night"]},
    "appetite changes": {"category": "General", "synonyms": ["appetite changes", "loss of appetite", "not hungry", "increased appetite"]},

    # 12. Mental and behavioral
    "anxiety": {"category": "Mental", "synonyms": ["anxiety", "anxious", "nervousness", "worry", "panic"]},
    "depression": {"category": "Mental", "synonyms": ["depression", "depressed", "feeling down", "hopeless"]},
    "mood swings": {"category": "Mental", "synonyms": ["mood swings"]},
    "irritability": {"category": "Mental", "synonyms": ["irritability", "irritable", "easily annoyed"]},
    "insomnia": {"category": "Mental", "synonyms": ["insomnia", "can't sleep", "trouble sleeping", "sleeplessness"]}
}

for k, v in SYMPTOM_ONTOLOGY.items():
    v["source"] = "Phase 7 Expansion"
    v["canonical"] = k
