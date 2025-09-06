import React, { useState } from 'react';
import { analyzeArticleText, analyzeArticleUrl } from './services/apiService';
import { AnalysisResult } from './types';
import './styles/App.css';

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | undefined>(undefined);
  const [articleText, setArticleText] = useState<string>('');
  const [articleUrl, setArticleUrl] = useState<string>('');
  const [analysisMode, setAnalysisMode] = useState<'manual-input' | 'url-input'>('manual-input');


  const handleAnalyzeClick = async () => {
    setIsLoading(true);
    setError(undefined);
    
    let response;
    
    if (analysisMode === 'manual-input') {
      if (!articleText.trim()) {
        setError('Please enter some article text to analyze');
        setIsLoading(false);
        return;
      }
      response = await analyzeArticleText(articleText);
    } else if (analysisMode === 'url-input') {
      if (!articleUrl.trim()) {
        setError('Please enter an article URL to analyze');
        setIsLoading(false);
        return;
      }
      response = await analyzeArticleUrl(articleUrl);
    }
    
    console.log('Backend Response:', response);
    
    setIsLoading(false);
    
    if (response) {
      if (response.success && response.result) {
        console.log('Updating result state:', response.result); //to debug
        setResult(response.result);
      } else {
        console.log('Error occurred:', response.error); //to debug
        setError(response.error || 'Failed to analyze article');
      }
    } else {
      setError('No response received');
    }
  };
  
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Fake News Detector</h1>
      </header>
      
      <main className="app-main">
        {/* Mode Selection */}
        <div className="mode-selection">
          <label>
            <input
              type="radio"
              value="manual-input"
              checked={analysisMode === 'manual-input'}
              onChange={(e) => setAnalysisMode(e.target.value as 'manual-input' | 'url-input')}
            />
            <span>Manual Input</span>
          </label>
          <label>
            <input
              type="radio"
              value="url-input"
              checked={analysisMode === 'url-input'}
              onChange={(e) => setAnalysisMode(e.target.value as 'manual-input' | 'url-input')}
            />
            <span>URL Input</span>
          </label>
        </div>

        {/* Article Input Field */}
        {analysisMode === 'manual-input' && (
          <div className="article-input-container">
            <label htmlFor="article-text">Enter article text to analyze:</label>
            <textarea
              id="article-text"
              className="article-textarea"
              value={articleText}
              onChange={(e) => setArticleText(e.target.value)}
              placeholder="Paste your article text here..."
              rows={8}
            />
            <p className="url-help-text">Paste or type the article content you want to analyze for fake news detection.</p>
          </div>
        )}

        {/* URL Input Field */}
        {analysisMode === 'url-input' && (
          <div className="article-input-container">
            <label htmlFor="article-url">Enter article URL to analyze:</label>
            <input
              id="article-url"
              type="url"
              className="article-url-input"
              value={articleUrl}
              onChange={(e) => setArticleUrl(e.target.value)}
              placeholder="https://example.com/article..."
            />
            <p className="url-help-text">The system will automatically scrape and analyze the article content from the provided URL.</p>
          </div>
        )}

        
        {isLoading && <p className="loading-message">Analyzing article...</p>}
        
        {result && !isLoading && (
          <div className={`result-container ${result.prediction.toLowerCase()}`}>
            <h2>Article appears to be {result.prediction}</h2>
            
            {result.prediction === 'Fake' && result.importantWords.length > 0 && (
              <div className="important-words">
                <h3>Top contributing words:</h3>
                <ul>
                  {result.importantWords.map((word, index) => (
                    <li key={index}>{word}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {error && <p className="error-message">{error}</p>}
        
        <button 
          className="analyze-button" 
          onClick={handleAnalyzeClick}
          disabled={isLoading}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Article'}
        </button>

        <footer className="app-footer">
            <p className="model-accuracy">Model Accuracy: 94.71%</p>         
        </footer>
      </main>
    </div>
  );
};

export default App;
