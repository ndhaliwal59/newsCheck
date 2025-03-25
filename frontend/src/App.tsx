import React, { useState, useEffect } from 'react';
import { analyzeCurrentPage } from './services/apiService';
import { AnalysisResult } from './types';
import './styles/App.css';

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | undefined>(undefined);


  const handleAnalyzeClick = async () => {
    setIsLoading(true);
    setError(undefined);
    
    const response = await analyzeCurrentPage();
    console.log('Backend Response:', response);
    
    setIsLoading(false);
    
    if (response.success && response.result) {
      console.log('Updating result state:', response.result); //to debug
      setResult(response.result);
    } else {
      console.log('Error occurred:', response.error); //to debug
      setError(response.error || 'Failed to analyze article');
    }
  };
  
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Fake News Detector</h1>
      </header>
      
      <main className="app-main">
        {!result && !isLoading && (
          <p className="intro-message">Press the button to analyze this article</p>
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
