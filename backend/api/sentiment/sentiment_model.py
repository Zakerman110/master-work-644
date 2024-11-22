import os
import re
import pickle
import numpy as np
from nltk.stem import PorterStemmer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from googletrans import Translator  # Import the translator

from api.models import MLModel

translator = Translator()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load pre-trained models and utilities
with open(os.path.join(BASE_DIR, 'tokenizer_balanced.pkl'), 'rb') as f:
    tokenizer = pickle.load(f)

# Load Active Model from Database
try:
    active_model = MLModel.objects.get(is_active=True)
    lstm_model_path = os.path.join(BASE_DIR, active_model.file_name)
    # lstm_model_path = os.path.join(BASE_DIR, 'lstm_model_balanced.h5')
    lstm_model = load_model(lstm_model_path)
    print(f"Loaded active model: {active_model.file_name}")
except MLModel.DoesNotExist:
    raise Exception("No active model found in the database. Please activate a model.")

label_encoder = LabelEncoder()
label_encoder.classes_ = np.load(os.path.join(BASE_DIR, 'classes.npy'), allow_pickle=True)

stop_words= ['yourselves', 'between', 'whom', 'itself', 'is', "she's", 'up', 'herself', 'here', 'your', 'each',
             'we', 'he', 'my', "you've", 'having', 'in', 'both', 'for', 'themselves', 'are', 'them', 'other',
             'and', 'an', 'during', 'their', 'can', 'yourself', 'she', 'until', 'so', 'these', 'ours', 'above',
             'what', 'while', 'have', 're', 'more', 'only', "needn't", 'when', 'just', 'that', 'were', "don't",
             'very', 'should', 'any', 'y', 'isn', 'who',  'a', 'they', 'to', 'too', "should've", 'has', 'before',
             'into', 'yours', "it's", 'do', 'against', 'on',  'now', 'her', 've', 'd', 'by', 'am', 'from',
             'about', 'further', "that'll", "you'd", 'you', 'as', 'how', 'been', 'the', 'or', 'doing', 'such',
             'his', 'himself', 'ourselves',  'was', 'through', 'out', 'below', 'own', 'myself', 'theirs',
             'me', 'why', 'once',  'him', 'than', 'be', 'most', "you'll", 'same', 'some', 'with', 'few', 'it',
             'at', 'after', 'its', 'which', 'there','our', 'this', 'hers', 'being', 'did', 'of', 'had', 'under',
             'over','again', 'where', 'those', 'then', "you're", 'i', 'because', 'does', 'all']
ps = PorterStemmer()


def preprocess_review(review):
    review = re.sub('[^a-zA-Z]', ' ', review)
    review = review.split()
    review = [ps.stem(word) for word in review if word not in stop_words]
    return ' '.join(review)


def translate_to_english(text):
    try:
        translated = translator.translate(text, src='auto', dest='en')
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def predict_sentiment(review):
    """
    Predict sentiment for a given review text using the LSTM model.
    """
    review_in_english = translate_to_english(review)
    cleaned_review = preprocess_review(review_in_english)
    review_seq = tokenizer.texts_to_sequences([cleaned_review])
    review_padded = pad_sequences(review_seq, maxlen=32, padding='post', truncating='post')
    lstm_pred = lstm_model.predict(review_padded)
    confidence = max(lstm_pred[0])
    lstm_sentiment = label_encoder.inverse_transform(np.argmax(lstm_pred, axis=1))
    return lstm_sentiment[0], confidence
