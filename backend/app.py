from flask import Flask, request, jsonify
from flask_cors import CORS
from news_classifier import NewsClassifier
from news_scraper import NewsScraper
from flask import jsonify

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Initialize models
classifier = NewsClassifier()
scraper = NewsScraper()

@app.route('/', methods=['GET'])
def home():
    print("HOME ROUTE ACCESSED")
    return "Welcome to the Fake News Detector API!"

@app.route('/api/analyze', methods=['POST'])
def analyze_article():
    try:
        print("=============== ANALYZE ROUTE TRIGGERED ===============") 
        print("Received request for /api/analyze")
        data = request.json
        
        # Option 1: Use content directly from extension
        if data.get('content'):
            content = data['content']
        # Option 2: Use URL to scrape content (preferred for better scraping)
        elif data.get('url'):
            article = scraper.scrape_article(data['url'])
            if not article or not article.get('content'):
                return jsonify({
                    'success': False,
                    'error': 'Failed to extract content from URL'
                }), 400
            content = article.get('content')
        else:
            return jsonify({
                'success': False,
                'error': 'No content or URL provided'
            }), 400
        
        # Classify the content
        prediction, important_words = classifier.predict(content)
        print(f"Prediction: {prediction}")
        
        return jsonify({
            'prediction': prediction,
            'importantWords': important_words
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Server is starting up...")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
