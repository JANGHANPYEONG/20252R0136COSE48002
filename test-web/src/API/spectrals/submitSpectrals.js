// src/API/spectrals/submitSpectrals.js
import { apiIP } from '../../config'; // ※ 프로젝트에 따라 default export라면: `import apiIP from '../../config'`

/**
 * 사용자가 입력한 파장 리스트를 백엔드로 전송
 * @param {number[]} wavelengthsNm - 예: [430, 450, 470, 490]
 * @param {string} endpoint - 필요하면 바꿔 쓰세요 (기본: /hsi/spectrals)
 * @returns {Promise<any>} 서버 응답 JSON
 */
export async function submitSpectrals(wavelengthsNm, endpoint = '/spectral/spectral-info/bulk') {
  // 중복 제거 + 정수 변환 + 유효값만 (300~1100nm 가드, 필요 시 조정)
  const clean = [];
  const seen = new Set();
  wavelengthsNm.forEach((w) => {
    const n = Number.parseInt(String(w).trim(), 10);
    if (!Number.isNaN(n) && n >= 300 && n <= 1100 && !seen.has(n)) {
      seen.add(n);
      clean.push(n);
    }
  });

  // JSON 페이로드: 사용자가 입력한 순서를 spectral_index로 그대로 부여 (0부터)
  const payload = {
    spectrals: clean.map((wl, i) => ({
      spectral_index: i,
      // 숫자는 JSON 직렬화 시 430.0 -> 430 으로 보일 수 있지만 타입은 number 입니다.
      // 서버에서 꼭 430.0 형태의 문자열을 원한다면 아래처럼 바꿔주세요:
      // wavelength_nm: Number(wl.toFixed(1)),
      wavelength_nm: wl,
    })),
  };

  const res = await fetch(`http://${apiIP}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || '스펙트럴 전송 실패');
  }
  return res.json().catch(() => ({}));
}
