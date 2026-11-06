import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from ml.preprocessing import normalize_symptom_list, map_common_tamil_tanglish

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset', 'symptoms_dataset.json')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved_model')
MODEL_PATH = os.path.join(MODEL_DIR, 'symptom_department_model.joblib')


def build_dataset():
    data = [
        {'symptoms': 'fever headache weakness', 'department': 'General Medicine'},
        {'symptoms': 'cough fever cold sore throat', 'department': 'General Medicine'},
        {'symptoms': 'stomach pain nausea vomiting diarrhea', 'department': 'Gastroenterology'},
        {'symptoms': 'skin rash itching irritation', 'department': 'Dermatology'},
        {'symptoms': 'joint pain knee pain swelling', 'department': 'Orthopedics'},
        {'symptoms': 'tooth pain cavity gum pain', 'department': 'Dentistry'},
        {'symptoms': 'eye pain redness blurred vision', 'department': 'Ophthalmology'},
        {'symptoms': 'ear pain hearing loss infection', 'department': 'ENT'},
        {'symptoms': 'stomach discomfort gas indigestion', 'department': 'Gastroenterology'},
        {'symptoms': 'skin irritation rash itching', 'department': 'Dermatology'},
        {'symptoms': 'back pain joint pain mobility', 'department': 'Orthopedics'},
        {'symptoms': 'cough chest pain breathing issues', 'department': 'General Medicine'},
        {'symptoms': 'headache dizziness fever', 'department': 'General Medicine'},
        {'symptoms': 'eye redness watery eyes irritation', 'department': 'Ophthalmology'},
        {'symptoms': 'ear ache ringing hearing problem', 'department': 'ENT'},
        {'symptoms': 'dental pain tooth ache gum swelling', 'department': 'Dentistry'},
        {'symptoms': 'fever body pain cough', 'department': 'General Medicine'},
        {'symptoms': 'sore throat cough fever', 'department': 'General Medicine'},
        {'symptoms': 'rash skin itch', 'department': 'Dermatology'},
        {'symptoms': 'knee pain swelling walking pain', 'department': 'Orthopedics'},
        {'symptoms': 'pain in stomach after food', 'department': 'Gastroenterology'},
        {'symptoms': 'pain in eyes blurry vision', 'department': 'Ophthalmology'},
        {'symptoms': 'toshi vena', 'department': 'General Medicine'},
        {'symptoms': 'jwaram thalai vali', 'department': 'General Medicine'},
        {'symptoms': 'skin irritations and itching', 'department': 'Dermatology'},
        {'symptoms': 'vaai soga', 'department': 'Gastroenterology'},
    ]

    df = pd.DataFrame(data)
    df['cleaned'] = df['symptoms'].apply(lambda x: ' '.join(normalize_symptom_list([map_common_tamil_tanglish(symptom) for symptom in str(x).split()])))
    return df


def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = build_dataset()
    X = df['cleaned']
    y = df['department']
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    pipeline.fit(X_train, y_train)
    score = pipeline.score(X_test, y_test)
    print(f'Model accuracy: {score:.3f}')
    print(classification_report(y_test, pipeline.predict(X_test)))

    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        json.dump(df.to_dict(orient='records'), f, ensure_ascii=False, indent=2)

    import joblib
    joblib.dump(pipeline, MODEL_PATH)
    return {'accuracy': score, 'model_path': MODEL_PATH}


if __name__ == '__main__':
    train_model()
