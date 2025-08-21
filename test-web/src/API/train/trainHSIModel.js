import { apiIP } from '../../config';

/**
 * HSI 학습 모델 훈련을 시작하는 API
 * @param {Array<string>} idList - 학습에 사용할 육류 ID 리스트 (예: ["meat_id_1", "meat_id_2", "meat_id_3"])
 * @returns {Promise<Object>} 학습 시작 응답
 * {
 *   "message": "HSI training started in background for 3 images",
 *   "train_id": "uuid-string",
 *   "process_pid": 12345,
 *   "created_at": "2024-01-01T00:00:00"
 * }
 */
export const trainHSIModel = async (idList) => {
  try {
    // 요청 데이터 구성
    const requestData = {
      id_list: idList
    };

    // API 호출
    const response = await fetch(`http://${apiIP}/train/hsi`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    // 응답 로깅 (디버깅용)
    console.log('HSI Training API Response:', result);
    
    return result;
  } catch (error) {
    console.error('HSI Training API Error:', error);
    throw error;
  }
};

/**
 * HSI 학습 상태를 확인하는 API (선택사항)
 * @param {string} trainId - 학습 ID
 * @returns {Promise<Object>} 학습 상태 정보
 */
export const getHSITrainingStatus = async (trainId) => {
  try {
    const response = await fetch(`http://${apiIP}/train/hsi/status/${trainId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('HSI Training Status API Error:', error);
    throw error;
  }
};

export default trainHSIModel;
