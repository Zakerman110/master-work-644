import os
import numpy as np
import pandas as pd
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, SpatialDropout1D
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import one_hot, Tokenizer
from tensorflow.keras.callbacks import Callback, EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from sklearn.preprocessing import LabelEncoder
import pickle

from api.models import MLModel
from api.sentiment.sentiment_model import translate_to_english

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def train_new_model(reviews):
    """
    Train a new LSTM model using the provided reviews.
    Save the model and its tokenizer, and update the MLModel database.
    """

    existing_df = pd.read_csv(os.path.join(BASE_DIR, 'process_reviews.csv'))

    # Prepare review texts and labels
    texts = [translate_to_english(review.text) for review in reviews]
    labels = [review.human_sentiment for review in reviews]

    # Load the new reviews into DataFrame
    new_reviews = pd.DataFrame({
        "reviews": texts,
        "sentiment": labels
    })

    # Load the saved LabelEncoder
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.load(os.path.join(BASE_DIR, 'classes.npy'), allow_pickle=True)

    # Encode sentiments in the new reviews using the existing LabelEncoder
    new_reviews['sentiment'] = label_encoder.transform(new_reviews['sentiment'])

    # Add additional fields to the new reviews
    new_reviews['review_len'] = new_reviews['reviews'].str.len()
    new_reviews['word_count'] = new_reviews['reviews'].str.split().str.len()

    # Append the new reviews to the existing DataFrame
    updated_df = pd.concat([existing_df, new_reviews], ignore_index=True)
    updated_df['reviews'] = updated_df['reviews'].astype("str")

    # Parameters
    NUM_WORDS = 30000
    MAX_SEQUENCE_LENGTH = 32
    OOV_TOKEN = '<OOV>'
    PADDING = 'post'

    # Preprocess Reviews
    with open(os.path.join(BASE_DIR, 'tokenizer.pkl'), 'rb') as f:
        tokenizer = pickle.load(f)
    X_seq = tokenizer.texts_to_sequences(updated_df['reviews'])
    X_seq = pad_sequences(X_seq, maxlen=MAX_SEQUENCE_LENGTH, padding=PADDING, truncating=PADDING)

    Y_seq = pd.get_dummies(updated_df['sentiment']).values

    X_train, X_test, Y_train, Y_test = train_test_split(X_seq, Y_seq, test_size=0.25, random_state=0)

    # Compute class weights
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(updated_df['sentiment']),
        y=updated_df['sentiment']
    )
    class_weights = dict(enumerate(class_weights))

    # Build LSTM Model
    model = Sequential([
        Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=32, input_length=MAX_SEQUENCE_LENGTH),
        SpatialDropout1D(0.5),
        LSTM(100, dropout=0.2, recurrent_dropout=0.2),
        Dense(512, activation='relu'),
        Dropout(0.8),
        Dense(256, activation='relu'),
        Dropout(0.8),
        Dense(Y_train.shape[1], activation='softmax')
    ])

    model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

    # Train the model
    history = model.fit(
        X_train, Y_train,
        validation_split=0.2,
        epochs=25,
        batch_size=16,
        class_weight=class_weights,
        callbacks=[
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2)
        ]
    )

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(Y_test.argmax(axis=1), y_pred.argmax(axis=1))
    precision = precision_score(Y_test.argmax(axis=1), y_pred.argmax(axis=1), average='weighted')
    recall = recall_score(Y_test.argmax(axis=1), y_pred.argmax(axis=1), average='weighted')
    f1 = f1_score(Y_test.argmax(axis=1), y_pred.argmax(axis=1), average='weighted')

    # Save the model
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = f'lstm_model_{timestamp}.h5'

    model.save(os.path.join(BASE_DIR, model_filename))

    # Save metadata to database
    ml_model = MLModel.objects.create(
        file_name=model_filename,
        created_at=datetime.now(),
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        is_active=False  # Newly trained models are not active by default
    )

    # Associate the reviews with the new model
    ml_model.reviews.add(*[review.id for review in reviews])

    return ml_model
