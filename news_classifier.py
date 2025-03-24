import joblib

class NewsClassifier:
    def __init__(self, model_path='fake_news_detector.pkl'):
        # Load the model
        saved_data = joblib.load(model_path)
        self.vectorizer = saved_data['vectorizer']
        self.model = saved_data['model']
    
    def predict(self, text):
        """
        Predicts if a news article is fake or real
        
        Args:
            text (str): The news article text
            
        Returns:
            str: "Fake" or "Real"
        """
        transformed_text = self.vectorizer.transform([text])
        prediction = self.model.predict(transformed_text)[0]
        return "Fake" if prediction else "Real"
