/**
 * 이력번호와 샘플번호로부터 20자리 해시 ID를 생성하는 함수
 * @param {string} traceNum - 이력번호 (예: "140119100857")
 * @param {string} sampleNum - 샘플번호 (예: "S1", "1")
 * @returns {Promise<string>} - 20자리 해시 ID
 */
export const generateHashId = async (traceNum, sampleNum) => {
  // 샘플번호의 S 문자 제거 (S1 -> 1, s2 -> 2)
  const cleanSampleNum = sampleNum.toString().replace(/[sS]/g, '');
  
  // 이력번호 + 샘플번호 조합
  const combinedString = `${traceNum}-${cleanSampleNum}`;
  
  // SHA-256 해시
  const encoder = new TextEncoder();
  const data = encoder.encode(combinedString);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  
  // 해시를 16진수 문자열로 변환
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  
  // 처음 20자리만 사용
  return hashHex.substring(0, 20);
};

/**
 * 파장대의 spectral_index를 반환하는 함수
 * @param {string} wavelength - 파장대 (예: "430nm", "540nm", "rgb")
 * @returns {number} - spectral_index (430nm=0, 540nm=1, rgb=0 등)
 */
export const getSpectralIndex = (wavelength) => {
  const wl = wavelength.toLowerCase();
  
  if (wl === '430nm') return 0;
  if (wl === '540nm') return 1;
  if (wl === '640nm') return 2;
  if (wl === '740nm') return 3;
  if (wl === 'rgb') return 0; // RGB는 0으로 설정
  
  // 기타 파장대는 범위로 분류
  const match = wl.match(/(\d+)nm/);
  if (match) {
    const nmValue = parseInt(match[1]);
    if (nmValue <= 450) return 0;
    if (nmValue <= 600) return 1;
    if (nmValue <= 700) return 2;
    return 3;
  }
  
  return 0; // 기본값
};