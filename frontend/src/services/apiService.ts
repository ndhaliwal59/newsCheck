import { AnalysisResult } from '../types';

const API_URL = 'http://localhost:5001/api';

export const analyzeCurrentPage = async (): Promise<{
  success: boolean;
  result?: AnalysisResult;
  error?: string;
}> => {
  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab.id) {
      return { success: false, error: 'No active tab found' };
    }
    
    // Extract page content using Chrome scripting API
    const [{ result: pageContent }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        // Get all paragraph text as a simple approach
        const paragraphs = Array.from(document.querySelectorAll('p'));
        return paragraphs.map(p => p.innerText).join(' ');
      }
    });
    
    // Send content to backend for analysis
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        url: tab.url,
        content: pageContent 
      }),
    });
    
    const data = await response.json();
    return { success: true, result: data };
    
  } catch (error) {
    console.error('Error analyzing page:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }
};
