from flask import Flask, render_template, request, jsonify
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from functools import lru_cache
import logging
from datetime import datetime


app = Flask(__name__)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')


lemmatizer = WordNetLemmatizer()


def load_resource(file_path, load_method, encoding=None):
    try:
        if encoding:
            with open(file_path, 'r', encoding=encoding) as f:
                return load_method(f)
        with open(file_path, 'rb') as f:
            return load_method(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        raise

try:
    intents = load_resource('intents.json', json.load, encoding='utf-8')
    words = load_resource('words.pkl', pickle.load)
    classes = load_resource('classes.pkl', pickle.load)
    model = load_model('chatbot_model.h5')
except Exception as e:
    logger.critical(f"Failed to initialize chatbot: {str(e)}")
    raise

@lru_cache(maxsize=1000)
def clean_up_sentence(sentence):
    try:
        sentence_words = nltk.word_tokenize(sentence, language='english', preserve_line=True)
        return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    except Exception as e:
        logger.error(f"Error cleaning sentence: {str(e)}")
        return []

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = np.zeros(len(words), dtype=np.float32)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return bag

def predict_class(sentence):
    try:
        bow = bag_of_words(sentence)
        res = model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return [{
            'intent': classes[r[0]],
            'probability': float(r[1]),
            'timestamp': datetime.now().isoformat()
        } for r in results]
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return []

def get_response(intents_list):
    if not intents_list:
        return random.choice([
            "I'm not sure I understand. Could you rephrase that?",
            "I didn't get that. Can you try asking differently?",
            "I'm still learning. Could you explain that another way?"
        ])
    
    tag = intents_list[0]['intent']
    for intent in intents['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['response'])
    
    return "I don't have a response for that yet. I'm still learning!"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        user_input = request.json.get('message', '').strip()
        if not user_input:
            return jsonify({'error': 'Message cannot be empty'}), 400
            
        logger.info(f"Received message: {user_input}")
        intents_list = predict_class(user_input)
        response = get_response(intents_list)
        
        return jsonify({
            'reply': response,
            'intent': intents_list[0]['intent'] if intents_list else None,
            'confidence': intents_list[0]['probability'] if intents_list else None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)



