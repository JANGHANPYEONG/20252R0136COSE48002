import React from 'react';
import { usePrediction } from '../context/PredictionContext';
import PredictionProgressModal from './PredictionProgressModal';
import PredictionResultModal from './PredictionResultModal';

const GlobalPredictionModals = () => {
  const {
    progressModalOpen,
    resultModalOpen,
    predictionProgress,
    predictionResults,
    isPredictionCompleted,
    closeProgressModal,
    closeResultModal,
  } = usePrediction();

  return (
    <>
      {/* 예측 진행 상황 모달 - 전역으로 표시 */}
      <PredictionProgressModal
        open={progressModalOpen}
        onClose={closeProgressModal}
        progress={predictionProgress}
        totalCount={predictionProgress.length}
        isCompleted={isPredictionCompleted}
        title="예측 진행 상황"
      />

      {/* 예측 결과 모달 - 전역으로 표시 */}
      <PredictionResultModal
        open={resultModalOpen}
        onClose={closeResultModal}
        results={predictionResults}
        title="예측 결과"
      />
    </>
  );
};

export default GlobalPredictionModals;
