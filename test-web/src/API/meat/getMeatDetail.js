// 상세 조회: POST /dashboard/dashboard/individual  (req: { id })
import { apiIP } from '../../config';

const DETAIL_ENDPOINT = `http://${apiIP}/dashboard/dashboard/individual`;

export async function getMeatDetail(id, signal) {
  const res = await fetch(DETAIL_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id }),
    signal,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Detail fetch failed (${res.status}): ${text}`);
  }
  return res.json();
}
