// 파장 정보 조회: GET /spectral/spectral-info
import { apiIP } from '../../config';

const SPECTRAL_INFO_ENDPOINT = `http://${apiIP}/spectral/spectral-info`;

export async function getSpectralInfo(signal) {
    const res = await fetch(SPECTRAL_INFO_ENDPOINT, {
        method: 'GET',
        signal,
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Spectral info fetch failed (${res.status}): ${text}`);
    }
    return res.json();
}
