export interface AnalysisResult {
  prediction: 'Real' | 'Fake';
  importantWords: string[];
}
