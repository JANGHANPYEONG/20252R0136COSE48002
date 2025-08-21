import { apiIP } from '../../config';

export async function updateMeatInfo(payload) {
  const response = await fetch(`http://${apiIP}/meat`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(text || 'Failed to update meat info');
  }
  return response.json();
}

export default updateMeatInfo;

