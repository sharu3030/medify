import re
import unicodedata


def normalize_text(text):
    if not isinstance(text, str):
        return ''
    text = text.lower().strip()
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_symptom_list(symptoms):
    normalized = []
    for symptom in symptoms:
        if not symptom:
            continue
        cleaned = normalize_text(symptom)
        if cleaned:
            normalized.append(cleaned)
    return normalized


def map_common_tamil_tanglish(symptom):
    replacements = {
        'fever': 'fever',
        'jwaram': 'fever',
        'kallal': 'fever',
        'headache': 'headache',
        'talukku': 'headache',
        'topa': 'headache',
        'cough': 'cough',
        'sore throat': 'sore throat',
        'throat pain': 'sore throat',
        'skin irritation': 'skin irritation',
        'rash': 'skin irritation',
        'stomach pain': 'stomach pain',
        'stomach discomfort': 'stomach pain',
        'gas': 'stomach pain',
        'joint pain': 'joint pain',
        'body pain': 'joint pain',
        'eye pain': 'eye pain',
        'ear pain': 'ear pain',
        'dental pain': 'dental pain',
        'tooth pain': 'dental pain',
        'vomiting': 'vomiting',
        'nausea': 'nausea',
        'dizziness': 'dizziness',
        'burning eyes': 'eye pain',
        'itching': 'skin irritation',
        'sore eye': 'eye pain',
        'ear ache': 'ear pain',
        'sneezing': 'cough'
    }
    text = normalize_text(symptom)
    for key, value in replacements.items():
        if key in text:
            return value
    return text
