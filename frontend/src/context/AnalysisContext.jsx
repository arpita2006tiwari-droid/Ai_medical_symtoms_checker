import React, { createContext, useContext, useState } from 'react';

const AnalysisContext = createContext(null);

export const AnalysisProvider = ({ children }) => {
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  
  // Helper to store result from predict/analyze
  const setAnalysisResult = (result) => {
    setCurrentAnalysis(result);
  };

  const clearAnalysis = () => {
    setCurrentAnalysis(null);
  };

  return (
    <AnalysisContext.Provider value={{ currentAnalysis, setAnalysisResult, clearAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => useContext(AnalysisContext);
