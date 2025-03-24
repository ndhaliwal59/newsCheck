import joblib
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

class NewsClassifier:
    def __init__(self, model_path='fake_news_detector.pkl'):
        # Load the model
        saved_data = joblib.load(model_path)
        self.vectorizer = saved_data['vectorizer']
        self.model = saved_data['model']
    
    def predict(self, text):
        transformed_text = self.vectorizer.transform([text])
        prediction = self.model.predict(transformed_text)[0]
        
        if prediction:  # If classified as Fake
            feature_importance = self.model.coef_[0]
            
            # Create a new vectorizer to get word counts from the input text
            count_vectorizer = CountVectorizer(vocabulary=self.vectorizer.get_feature_names_out())
            word_counts = count_vectorizer.fit_transform([text])
            
            # Get words that appear in the text
            words_in_text = [word for word, count in zip(count_vectorizer.get_feature_names_out(), word_counts.toarray()[0]) if count > 0]
            
            # Get word-importance pairs for words that appear in the text
            word_importance = [(word, importance) for word, importance in zip(self.vectorizer.get_feature_names_out(), feature_importance) if word in words_in_text]
            
            # Sort by importance (absolute value) in descending order
            sorted_words = sorted(word_importance, key=lambda x: abs(x[1]), reverse=True)
            
            # Get top 3 words contributing to "Fake" classification
            important_words = [word for word, _ in sorted_words[:3]]
        else:
            important_words = []
        
        return ("Fake" if prediction else "Real"), important_words
