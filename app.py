import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import requests
from ml.predict import predict_department

load_dotenv(Path(__file__).resolve().parent / '.env')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent'

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

HEALTH_FAQ = {
    'fever': 'Fever is a temporary rise in body temperature, often due to infection. Rest, stay hydrated, and monitor temperature. See a doctor if it exceeds 102°F (39°C), lasts more than 3 days, or comes with severe headache, stiff neck, rash, or breathing difficulty.',
    'cold': 'Common cold is a viral infection of the nose and throat. Rest, fluids, saline gargle, and over-the-counter relief can help. See a doctor if symptoms last over 10 days or worsen.',
    'cough': 'Cough clears irritants from your airways. Honey (for adults), fluids, and humidified air may soothe it. Seek care if it persists over 2-3 weeks, brings blood, or causes breathing trouble.',
    'headache': 'Common causes include tension, dehydration, lack of sleep, or migraine. Rest in a dark room, hydrate, and use a cool compress. Seek urgent care for sudden severe headache, confusion, or vision changes.',
    'stomach': 'Stomach discomfort may come from indigestion, gas, or infection. Eat light bland foods, stay hydrated, avoid spicy/fatty meals. See a doctor for severe pain, vomiting blood, black stools, or persistent symptoms.',
    'skin': 'Skin rashes or itching can result from allergy, infection, or irritation. Keep the area clean and dry, avoid scratching, and use mild moisturizer. See a doctor if it spreads, oozes, or is accompanied by fever.',
    'joint': 'Joint pain may stem from arthritis, injury, or overuse. Gentle movement, rest, ice/heat, and weight management can help. See a doctor for severe swelling, redness, or inability to move the joint.',
    'tooth': 'Tooth pain often means decay, infection, or gum disease. Rinse with warm salt water, avoid very hot/cold foods, and see a dentist promptly for persistent pain or swelling.',
    'eye': 'Eye irritation or redness may be from strain, allergy, or infection. Avoid rubbing, use clean water to rinse, and limit screen time. See an eye doctor for pain, vision loss, or discharge.',
    'ear': 'Ear pain can result from infection, wax buildup, or pressure changes. Avoid inserting objects into the ear. See a doctor for severe pain, hearing loss, or discharge.',
    'diabetes': 'Diabetes affects blood sugar. Common signs include increased thirst, frequent urination, and fatigue. It requires medical diagnosis and ongoing management — consult a doctor.',
    'blood pressure': 'High blood pressure often has no symptoms. Monitor regularly, reduce salt, exercise, and maintain a healthy weight. Consult a doctor for readings consistently above 130/80 mmHg.',
    'pregnancy': 'If you suspect pregnancy or have pregnancy-related concerns, consult an obstetrician/gynecologist for proper prenatal care.',
    'emergency': 'Chest pain, trouble breathing, severe bleeding, stroke signs (face drooping, arm weakness, speech difficulty), or severe allergic reaction require emergency care immediately.',
}

def local_health_reply(text):
    t = text.lower()
    for keyword, reply in HEALTH_FAQ.items():
        if keyword in t:
            return reply + '\n\nThis is general health information, not a medical diagnosis. Please consult a qualified doctor.'
    return ('I can share general information about common symptoms like fever, cold, cough, headache, stomach pain, skin rash, joint pain, tooth pain, eye/ear issues, diabetes, and blood pressure. '
            'Ask about one of these, or describe your concern. For serious or urgent symptoms, consult a qualified doctor immediately.')

@app.route('/')
def index():
    return render_template('find_hospitals.html')

@app.route('/find-hospitals')
def find_hospitals():
    return render_template('find_hospitals.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'application': 'MediFind AI'})

@app.route('/api/symptoms/analyze', methods=['POST'])
def analyze_symptoms():
    data = request.get_json(silent=True) or {}
    text = (data.get('symptoms') or '').strip()
    if not text:
        return jsonify({'success': False, 'message': 'Please enter symptoms.'}), 400
    result = predict_department(text)
    return jsonify({
        'success': True,
        'department': result.get('department', 'General Medicine'),
        'confidence': result.get('confidence', 0.0),
        'message': result.get('message', ''),
        'warning': result.get('warning', '')
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    lang = (data.get('lang') or 'en').strip()
    if not message:
        return jsonify({'success': False, 'message': 'Please provide a message.'}), 400

    # Try Gemini AI first if a key is configured
    if GEMINI_API_KEY:
        try:
            system_prompt = (
                'You are MediFind AI, a helpful healthcare assistant. '
                'Answer health-related questions clearly and safely. Do NOT diagnose diseases or prescribe medication. '
                'Always suggest consulting a qualified doctor for serious symptoms. '
                'Keep responses concise and friendly.'
            )
            if lang == 'ta':
                system_prompt += ' Respond in Tamil.'
            elif lang == 'te':
                system_prompt += ' Respond in Tanglish (Tamil written in English script).'

            payload = {
                'contents': [
                    {'role': 'user', 'parts': [{'text': f'{system_prompt}\n\nUser: {message}'}]}
                ],
                'generationConfig': {
                    'temperature': 0.7,
                    'maxOutputTokens': 512,
                }
            }
            headers = {'Content-Type': 'application/json'}
            resp = requests.post(f'{GEMINI_URL}?key={GEMINI_API_KEY}', json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                content = resp.json()
                candidates = content.get('candidates', [])
                if candidates:
                    text_reply = candidates[0].get('content', {}).get('parts', [{}])[0].get('text')
                    if text_reply:
                        return jsonify({'success': True, 'reply': text_reply})
        except Exception:
            pass  # fall through to local reply

    # Local health FAQ fallback (always works, no API key needed)
    reply = local_health_reply(message)
    return jsonify({'success': True, 'reply': reply, 'source': 'local'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
