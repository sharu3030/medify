import os
import joblib

from ml.preprocessing import normalize_symptom_list, map_common_tamil_tanglish

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'saved_model', 'symptom_department_model.joblib')

KEYWORD_DEPARTMENTS = [
    ({'fever', 'flu', 'cold', 'cough', 'headache', 'weakness', 'dizziness', 'sore throat', 'throat pain', 'body pain', 'common cold'}, 'General Medicine'),
    ({'stomach', 'stomach pain', 'abdominal', 'nausea', 'vomiting', 'diarrhea', 'indigestion', 'gas', 'belly pain'}, 'Gastroenterology'),
    ({'skin', 'rash', 'itching', 'irritation', 'allergy', 'dermatology'}, 'Dermatology'),
    ({'joint', 'knee', 'back pain', 'swelling', 'mobility', 'leg pain', 'hip pain'}, 'Orthopedics'),
    ({'tooth', 'dental', 'gum', 'jaw pain', 'teeth'}, 'Dentistry'),
    ({'eye', 'eyeball', 'vision', 'blur', 'redness', 'watering', 'eye pain'}, 'Ophthalmology'),
    ({'ear', 'hearing', 'ringing', 'ear pain', 'ear ache'}, 'ENT'),
]


def department_from_keywords(text):
    text = (text or '').lower().strip()
    for keywords, department in KEYWORD_DEPARTMENTS:
        for keyword in keywords:
            if keyword in text:
                return department
    return None


def _load_model_or_train():
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        try:
            from ml.train_model import train_model
            train_model()
            return joblib.load(MODEL_PATH)
        except Exception:
            return None


try:
    model = _load_model_or_train()
except Exception:
    model = None


def predict_department(symptoms):
    # Accept a list of symptom strings or a single string.
    if isinstance(symptoms, str):
        symptoms = [symptoms] if symptoms.strip() else []
    if not symptoms:
        return {
            'department': 'General Medicine',
            'confidence': 0.0,
            'message': 'No symptoms provided.',
            'warning': 'Please enter symptoms to receive preliminary guidance.'
        }

    normalized = []
    for symptom in symptoms:
        if not isinstance(symptom, str):
            continue
        cleaned = map_common_tamil_tanglish(symptom)
        normalized.append(cleaned)

    combined = ' '.join(normalize_symptom_list(normalized))
    if not combined:
        return {
            'department': 'General Medicine',
            'confidence': 0.2,
            'message': 'Could not interpret the entered symptoms.',
            'warning': 'Please enter clearer symptoms or seek professional advice.'
        }

    keyword_department = department_from_keywords(combined)
    if keyword_department:
        return {
            'department': keyword_department,
            'confidence': 0.82,
            'message': 'This is a preliminary department recommendation based on common symptom patterns.',
            'warning': 'This is preliminary guidance only and not a diagnosis.'
        }

    if model is None:
        keyword_to_department = {
            'fever': 'General Medicine',
            'cough': 'General Medicine',
            'headache': 'General Medicine',
            'stomach': 'Gastroenterology',
            'pain': 'General Medicine',
            'rash': 'Dermatology',
            'itching': 'Dermatology',
            'skin': 'Dermatology',
            'joint': 'Orthopedics',
            'eye': 'Ophthalmology',
            'ear': 'ENT',
            'tooth': 'Dentistry',
            'dental': 'Dentistry',
        }
        for keyword, department in keyword_to_department.items():
            if keyword in combined:
                return {
                    'department': department,
                    'confidence': 0.68,
                    'message': 'Some technical issue occurred while loading the trained model, so a safe fallback recommendation is shown.',
                    'warning': 'This is preliminary guidance only. Please consult a doctor for a full assessment.'
                }
        return {
            'department': 'General Medicine',
            'confidence': 0.58,
            'message': 'Some technical issue occurred while loading the trained model, so a safe fallback recommendation is shown.',
            'warning': 'This is preliminary guidance only. Please consult a doctor for a full assessment.'
        }

    pred = model.predict([combined])[0]
    proba = model.predict_proba([combined])[0]
    confidence = float(max(proba))

    if confidence < 0.35:
        pred = 'General Medicine'
        recommendation = 'Low confidence. Please consult a qualified doctor for an accurate assessment.'
        advice = 'This is preliminary guidance only. For persistent or severe symptoms, seek professional medical care immediately.'
    else:
        recommendation = 'This is a preliminary department recommendation only.'
        advice = 'The model is not a diagnosis tool and should not replace medical advice.'

    return {
        'department': pred,
        'confidence': round(confidence, 3),
        'message': recommendation,
        'warning': advice,
    }
