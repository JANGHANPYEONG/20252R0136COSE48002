import "firebase/firestore";
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth"; // 코드 추가
import { getFirestore } from "firebase/firestore";
import { getStorage, } from "firebase/storage";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

const firebaseConfig = {
  apiKey: process.env.REACT_APP_API_KEY,
  authDomain: process.env.REACT_AUTH_DOMAIN,
  projectId: process.env.REACT_PROJECT_ID,
  storageBucket: process.env.REACT_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_ID,
  measurementId: process.env.REACT_MEASUREMENT_ID
};

const firebase=initializeApp(firebaseConfig);
const app = initializeApp(firebaseConfig);
export const db=getFirestore(app);
export const fireStore=getFirestore(firebase);
export const auth = getAuth(app); // 코드 추가
// 고기 이미지 데이터 storage
export const storage = getStorage(app);