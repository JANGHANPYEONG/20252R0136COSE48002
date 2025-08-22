import React, { createContext, useContext, useState } from 'react';

const PredictionContext = createContext();

export const usePrediction = () => {
  const context = useContext(PredictionContext);
  if (!context) {
    throw new Error('usePrediction must be used within a PredictionProvider');
  }
  return context;
};

export const PredictionProvider = ({ children }) => {
  const [predictionProgress, setPredictionProgress] = useState([]);
  const [predictionResults, setPredictionResults] = useState([]);
  const [isPredictionCompleted, setIsPredictionCompleted] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [progressModalOpen, setProgressModalOpen] = useState(false);
  const [resultModalOpen, setResultModalOpen] = useState(false);

  const startPrediction = () => {
    setIsPredicting(true);
    setProgressModalOpen(true);
    setIsPredictionCompleted(false);
    setPredictionProgress([]);
    setPredictionResults([]);
  };

  const updateProgress = (progress, totalCount, completedCount) => {
    setPredictionProgress(progress);
  };

  const completePrediction = (results, progress) => {
    setPredictionResults(results || []);
    setPredictionProgress(progress || []);
    setIsPredictionCompleted(true);
    setIsPredicting(false);
    setProgressModalOpen(false);
    setResultModalOpen(true);
  };

  const closeProgressModal = () => {
    setProgressModalOpen(false);
  };

  const closeResultModal = () => {
    setResultModalOpen(false);
  };

  const resetPrediction = () => {
    setPredictionProgress([]);
    setPredictionResults([]);
    setIsPredictionCompleted(false);
    setIsPredicting(false);
    setProgressModalOpen(false);
    setResultModalOpen(false);
  };

  const value = {
    predictionProgress,
    predictionResults,
    isPredictionCompleted,
    isPredicting,
    progressModalOpen,
    resultModalOpen,
    startPrediction,
    updateProgress,
    completePrediction,
    closeProgressModal,
    closeResultModal,
    resetPrediction,
  };

  return (
    <PredictionContext.Provider value={value}>
      {children}
    </PredictionContext.Provider>
  );
};
