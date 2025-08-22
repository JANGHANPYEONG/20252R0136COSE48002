import { getIdToken } from 'firebase/auth';
import { auth } from '../firebase-config';

export default async function fetchWithAuth(url, options = {}) {
  const token = auth.currentUser ? await getIdToken(auth.currentUser, false) : null;
  const headers = {
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    'Content-Type': (options.headers && options.headers['Content-Type']) || 'application/json',
  };
  return fetch(url, { ...options, headers });
}
