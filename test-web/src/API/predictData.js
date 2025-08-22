// src/api/predictData.js

import { apiIP } from '../config'; // 백엔드 ML 서버 주소

// 개별 데이터 상세 정보 가져오기
const fetchIndividualData = async (id) => {
  try {
    const response = await fetch(`http://${apiIP}/dashboard/dashboard/individual`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id }),
    });

    if (!response.ok) {
      throw new Error(`개별 데이터 조회 실패: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`개별 데이터 조회 실패 (ID: ${id}):`, error);
    throw error;
  }
};

// 단일 예측 API 호출
const predictSingleItem = async (id, seqno, isRefrigerated) => {
  try {
    const response = await fetch(`http://${apiIP}/hsipredict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id,
        seqno,
        isRefrigerated
      }),
    });

    if (!response.ok) {
      throw new Error(`예측 API 실패: ${response.status}`);
    }

    const result = await response.json();
    return {
      ...result,
      id,
      seqno,
      isRefrigerated,
      status: 'completed',
      completedAt: new Date().toISOString()
    };
  } catch (error) {
    console.error(`예측 실패 (ID: ${id}, seqno: ${seqno}):`, error);
    return {
      id,
      seqno,
      isRefrigerated,
      status: 'failed',
      error: error.message,
      completedAt: new Date().toISOString()
    };
  }
};

// 메인 예측 함수
export const fetchPrediction = async (selectedRows, originalData, onProgressUpdate) => {
  try {
    const results = [];
    const progress = [];
    let totalItems = 0;
    let completedItems = 0;

    // 먼저 모든 예측 항목을 파악하고 진행 상황 배열 초기화
    const allPredictionItems = [];

    for (let i = 0; i < selectedRows.length; i++) {
      const id = selectedRows[i];

      try {
        // 개별 데이터 조회
        const individualData = await fetchIndividualData(id);

        if (!individualData.by_seqno_and_condition || individualData.by_seqno_and_condition.length === 0) {
          // 데이터가 없는 경우 진행 상황에 추가
          allPredictionItems.push({
            id,
            seqno: null,
            isRefrigerated: null,
            hasData: false
          });
          continue;
        }

        // 각 seqno와 condition에 대해 예측 항목 추가
        for (const condition of individualData.by_seqno_and_condition) {
          const { seqno, isRefrigerated } = condition;
          allPredictionItems.push({
            id,
            seqno,
            isRefrigerated,
            hasData: true
          });
        }

      } catch (error) {
        console.error(`ID ${id} 데이터 조회 실패:`, error);
        // 에러가 발생한 경우 진행 상황에 추가
        allPredictionItems.push({
          id,
          seqno: null,
          isRefrigerated: null,
          hasData: false,
          error: error.message
        });
      }
    }

    // 모든 예측 항목을 "대기중" 상태로 진행 상황 배열 초기화
    totalItems = allPredictionItems.filter(item => item.hasData).length;
    console.log(`총 ${totalItems}개 예측 항목을 처리합니다.`);

    for (const item of allPredictionItems) {
      if (item.hasData) {
        progress.push({
          id: item.id,
          seqno: item.seqno,
          isRefrigerated: item.isRefrigerated,
          status: 'pending',
          message: `예측 대기 중... (seqno: ${item.seqno}, ${item.isRefrigerated ? '숙성' : '냉장'})`,
          hasData: true
        });
        console.log(`예측 항목 추가: ${item.id} (seqno: ${item.seqno}, ${item.isRefrigerated ? '숙성' : '냉장'})`);
      } else {
        progress.push({
          id: item.id,
          status: 'failed',
          error: item.error || '데이터 구조가 올바르지 않습니다.',
          seqno: null,
          isRefrigerated: null,
          hasData: false
        });
        console.log(`실패 항목 추가: ${item.id} - ${item.error || '데이터 구조 오류'}`);
      }
    }

    // 초기 진행 상황 업데이트 (모든 항목이 "대기중" 상태)
    if (onProgressUpdate) {
      console.log('초기 진행 상황 업데이트:', progress.length, '개 항목');
      onProgressUpdate([...progress], totalItems, completedItems);
    }

    // 이제 각 예측 항목을 순차적으로 처리
    console.log('예측 처리 시작...');
    for (let i = 0; i < progress.length; i++) {
      const progressItem = progress[i];

      // 데이터가 없는 항목은 건너뛰기
      if (!progressItem.hasData) {
        console.log(`건너뛰기: ${progressItem.id} (데이터 없음)`);
        continue;
      }

      console.log(`예측 시작: ${progressItem.id} (seqno: ${progressItem.seqno}, ${progressItem.isRefrigerated ? '숙성' : '냉장'})`);

      try {
        // 예측 API 호출
        const predictionResult = await predictSingleItem(
          progressItem.id,
          progressItem.seqno,
          progressItem.isRefrigerated
        );

        results.push(predictionResult);

        // 진행 상황 업데이트
        if (predictionResult.status === 'completed') {
          progressItem.status = 'completed';
          progressItem.message = '예측 완료';
          progressItem.predictions = predictionResult.predictions;
          progressItem.xai_image_urls = predictionResult.xai_image_urls;
          progressItem.created_at = predictionResult.created_at;
          completedItems++;
          console.log(`예측 완료: ${progressItem.id} (${completedItems}/${totalItems})`);
        } else {
          progressItem.status = 'failed';
          progressItem.error = predictionResult.error;
          progressItem.message = '예측 실패';
          console.log(`예측 실패: ${progressItem.id} - ${predictionResult.error}`);
        }

        // 진행 상황 업데이트 콜백 호출 (각 예측 완료 시마다)
        if (onProgressUpdate) {
          onProgressUpdate([...progress], totalItems, completedItems);
        }

      } catch (error) {
        console.error(`예측 실패 (ID: ${progressItem.id}, seqno: ${progressItem.seqno}):`, error);
        progressItem.status = 'failed';
        progressItem.error = error.message;
        progressItem.message = '예측 실패';

        // 진행 상황 업데이트 콜백 호출
        if (onProgressUpdate) {
          onProgressUpdate([...progress], totalItems, completedItems);
        }
      }
    }

    return {
      results,
      progress,
      totalCount: totalItems,
      completedCount: completedItems,
      failedCount: totalItems - completedItems
    };

  } catch (error) {
    console.error('예측 프로세스 실패:', error);
    throw error;
  }
};

// 단일 예측 (테스트용)
export const predictSingle = async (id, seqno, isRefrigerated) => {
  return await predictSingleItem(id, seqno, isRefrigerated);
};
