// (로그인/로그아웃/토큰 헬퍼)

import { auth } from './firebase-config';
import {
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  getIdToken,
} from 'firebase/auth';

export const login = (email, password) =>
  signInWithEmailAndPassword(auth, email, password);

export const logout = () => signOut(auth);

export const watchAuth = (cb) => onAuthStateChanged(auth, cb);

export const getAuthToken = async () => {
  const user = auth.currentUser;
  if (!user) return null;
  return await getIdToken(user, false); // false: 캐시 사용, 만료 시 자동 갱신
};
