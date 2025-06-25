import 'firebase/firestore';
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth'; // 코드 추가
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// const firebaseConfig = {
//   apiKey: process.env.REACT_APP_API_KEY,
//   authDomain: process.env.REACT_APP_AUTH_DOMAIN,
//   projectId: process.env.REACT_APP_PROJECT_ID,
//   storageBucket: process.env.REACT_APP_STORAGE_BUCKET,
//   messagingSenderId: process.env.REACT_APP_MESSAGING_SENDER_ID,
//   appId: process.env.REACT_APP_ID,
//   measurementId: process.env.REACT_APP_MEASUREMENT_ID,
// };

const firebaseConfig = {
  apiKey: "AIzaSyB8neVkYr8xiD-V8QxXovkiLD4UzWeMapk",
  authDomain: "r0136cose48002.firebaseapp.com",
  projectId: "r0136cose48002",
  storageBucket: "r0136cose48002.firebasestorage.app",
  messagingSenderId: "880708399922",
  appId: "1:880708399922:web:47bdbe9ac704c3ffe8dd2b",
  measurementId: "G-DV8K5S2K9D"
};



const firebase = initializeApp(firebaseConfig);
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const fireStore = getFirestore(firebase);
export const auth = getAuth(app); // 코드 추가
// 고기 이미지 데이터 storage
export const storage = getStorage(app);
