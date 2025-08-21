// C:\KKM\산학협력\frontend\test-web\src\components\LogIn\LogInField.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// ✅ Firebase Auth: v9 모듈식 + 지속성 설정
import {
  signInWithEmailAndPassword,
  setPersistence,
  browserLocalPersistence,
  browserSessionPersistence,
} from 'firebase/auth';
import { auth } from '../../firebase-config'; // ✅ 중앙화된 auth 사용

// ✅ 토큰 자동 첨부 fetch 래퍼 & 서버 주소
import fetchWithAuth from '../../API/fetchWithAuth';
import { apiIP } from '../../config';

import { useSetUser } from '../../Utils/UserContext';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Typography from '@mui/material/Typography';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';

import layer_1 from '../../src_assets/layer_1.png';
import background from '../../src_assets/background.png';

const defaultTheme = createTheme();

const LogInField = () => {
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState(''); // 폼 검증/일반 에러 텍스트
  const [rememberMe, setRememberMe] = useState(false);

  // 🔔 팝업(Dialog) 상태
  const [errorDialogOpen, setErrorDialogOpen] = useState(false);
  const [errorDialogTitle, setErrorDialogTitle] = useState('');
  const [errorDialogMessage, setErrorDialogMessage] = useState('');

  const setUser = useSetUser();
  const navigate = useNavigate();

  // 저장된 이메일 복원
  useEffect(() => {
    const storedEmail = localStorage.getItem('rememberedEmail');
    if (storedEmail) {
      setLoginEmail(storedEmail);
      setRememberMe(true);
    }
  }, []);

  // 공통 팝업 오픈 함수
  const openErrorDialog = (title, message) => {
    setErrorDialogTitle(title);
    setErrorDialogMessage(message);
    setErrorDialogOpen(true);
  };

  // Firebase 에러 코드 → 메시지 매핑
  const firebaseErrorToMessage = (code) => {
    switch (code) {
      case 'auth/user-not-found':
        return '존재하지 않는 계정입니다. 이메일을 확인해주세요.';
      case 'auth/wrong-password':
        return '비밀번호가 일치하지 않습니다.';
      case 'auth/too-many-requests':
        return '로그인을 너무 많이 시도했습니다. 잠시 후 다시 시도해주세요.';
      case 'auth/invalid-email':
        return '올바른 이메일 형식이 아닙니다.';
      case 'auth/network-request-failed':
        return '네트워크 오류로 Firebase 로그인 요청이 실패했습니다.';
      case 'auth/invalid-api-key':
      case 'auth/invalid-auth-domain':
        return 'Firebase 설정(API Key/Auth Domain) 오류가 있습니다. 환경변수를 확인해주세요.';
      default:
        return 'Firebase 로그인 중 알 수 없는 오류가 발생했습니다.';
    }
  };

  // ✅ 메인 로그인 플로우
  const login = async () => {
    localStorage.setItem('isLoggedIn', 'false');
    // 0) 프론트 입력 검증
    if (!loginEmail) {
      setLoginError('아이디를 입력해주세요.');
      return;
    }
    if (!loginPassword) {
      setLoginError('비밀번호를 입력해주세요.');
      return;
    }
    setLoginError('');

    // 1) Firebase 인증 단계
    try {
      await setPersistence(
        auth,
        rememberMe ? browserLocalPersistence : browserSessionPersistence
      );
      await signInWithEmailAndPassword(auth, loginEmail, loginPassword);
    } catch (fbErr) {
      console.error('[AUTH ERROR]', fbErr?.code, fbErr?.message);
      const msg = firebaseErrorToMessage(fbErr?.code);
      openErrorDialog('Firebase 로그인 실패', msg);
      return; // Firebase 단계에서 실패하면 더 진행하지 않음
    }

    // // 2) 백엔드 토큰 검증 + 프로필/권한 조회 단계
    // let meRes;
    // try {
    //   meRes = await fetchWithAuth(`http://${apiIP}/auth/me`);
    // } catch (netErr) {
    //   console.error('[ME NETWORK ERROR]', netErr);
    //   openErrorDialog(
    //     '백엔드 연결 실패',
    //     '서버에 연결할 수 없습니다. (백엔드 미가동, 주소 오타, 또는 CORS 문제일 수 있습니다.)'
    //   );
    //   return;
    // }

    // if (!meRes.ok) {
    //   console.error('[ME HTTP ERROR]', meRes.status);
    //   // 상태코드별 분기
    //   if (meRes.status === 401) {
    //     openErrorDialog(
    //       '백엔드 인증 실패 (401)',
    //       '인증 토큰이 유효하지 않습니다. Firebase 프로젝트 불일치, 만료, 또는 헤더 누락일 수 있습니다.'
    //     );
    //   } else if (meRes.status === 403) {
    //     openErrorDialog(
    //       '권한 없음 (403)',
    //       '권한이 없습니다. 관리자에게 문의하세요.'
    //     );
    //   } else if (meRes.status === 404) {
    //     openErrorDialog(
    //       '사용자 DB 없음 (404)',
    //       'Firebase에는 로그인되었지만, 내부 DB에 사용자 정보가 없습니다.'
    //     );
    //   } else if (meRes.status >= 500) {
    //     openErrorDialog(
    //       '백엔드 서버 오류',
    //       `서버에서 오류가 발생했습니다. (status: ${meRes.status})`
    //     );
    //   } else {
    //     openErrorDialog(
    //       '요청 실패',
    //       `요청이 실패했습니다. (status: ${meRes.status})`
    //     );
    //   }
    //   return;
    // }

    // // 3) 비즈니스 권한 체크
    // const me = await meRes.json(); // { userId, name, type, ... }
    // if (!me.type || me.type === 'Normal') {
    //   openErrorDialog(
    //     '접근 권한 없음',
    //     '로그인 권한이 없습니다. 관리자에게 문의해주세요.'
    //   );
    //   return;
    // }
    // if (!me.userId) {
    //   openErrorDialog(
    //     'DB 사용자 정보 없음',
    //     'DB상 존재하지 않는 아이디입니다. 관리자에게 문의해주세요.'
    //   );
    //   return;
    // }

    // // 4) 전역 상태/스토리지 반영
    // setUser(me);
    // if (rememberMe) {
    //   localStorage.setItem('rememberedEmail', loginEmail);
    // } else {
    //   localStorage.removeItem('rememberedEmail');
    // }
    localStorage.setItem('isLoggedIn', 'true');

    // 5) 이동
    navigate('/Home', { replace: true });
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      if (event.target.name === 'email') {
        document.getElementById('password').focus();
      } else if (event.target.name === 'password') {
        login();
      }
    }
  };

  return (
    <ThemeProvider theme={defaultTheme}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          minWidth: '100vw',
          backgroundImage: `url(${background})`,
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
        }}
      >
        <CssBaseline />
        <img
          src={layer_1}
          alt=""
          style={{
            width: `${(323 / 1920) * 100}vw`,
            marginBottom: `${(48 / 1080) * 100}vh`,
          }}
        />
        <Box
          component="form"
          noValidate
          sx={{
            flexDirection: 'column',
            justifyContent: 'center',
            width: `${(450 / 1920) * 100}vw`,
            height: `${(594 / 1080) * 100}vh`,
            bgcolor: 'white',
            paddingX: `${(42 / 1920) * 100}vw`,
            borderRadius: `${(20 / 1920) * 100}vw`,
            mb: '160px',
          }}
        >
          <Typography
            sx={{
              alignSelf: 'center',
              textAlign: 'center',
              marginTop: `${(44 / 1080) * 100}vh`,
              marginBottom: `${(54 / 1080) * 100}vh`,
              color: '#616161',
              fontFamily: 'Google Sans',
              fontSize: `${(50 / 1080) * 100}vh`,
              fontStyle: 'normal',
              fontWeight: 400,
              lineHeight: 'normal',
            }}
          >
            Login
          </Typography>

          <input
            required
            id="email"
            type="email"
            placeholder="이메일을 입력하세요."
            name="email"
            autoComplete="email"
            autoFocus
            value={loginEmail}
            onChange={(e) => setLoginEmail(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{
              width: `${(365 / 1920) * 100}vw`,
              height: `${(72 / 1080) * 100}vh`,
              padding: '8px',
              marginBottom: `${(20 / 1080) * 100}vh`,
            }}
          />

          <input
            required
            id="password"
            type="password"
            placeholder="비밀번호를 입력하세요."
            name="password"
            autoComplete="current-password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{
              width: `${(365 / 1920) * 100}vw`,
              height: `${(72 / 1080) * 100}vh`,
              padding: '8px',
            }}
          />

          <FormControlLabel
            control={
              <Checkbox
                onChange={(e) => setRememberMe(e.target.checked)}
                color="primary"
                checked={rememberMe}
              />
            }
            label="아이디 저장"
          />

          {/* 폼 아래 작은 에러 텍스트 (입력 누락 등) */}
          {loginError && (
            <Typography variant="caption" color="error">
              {loginError}
            </Typography>
          )}
          <Button
            onClick={login}
            variant="contained"
            sx={{
              width: `${(366 / 1920) * 100}vw`,
              height: `${(64 / 1080) * 100}vh`,
              marginTop: `${(100 / 1080) * 100}vh`,
              mb: `${(44 / 1080) * 100}vh`,
              bgcolor: '#7BD758',
            }}
          >
            로그인
          </Button>
        </Box>
      </Box>

      {/* 🔔 오류 팝업 */}
      <Dialog open={errorDialogOpen} onClose={() => setErrorDialogOpen(false)}>
        <DialogTitle>{errorDialogTitle}</DialogTitle>
        <DialogContent>
          <Typography sx={{ whiteSpace: 'pre-line' }}>
            {errorDialogMessage}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setErrorDialogOpen(false)}>확인</Button>
        </DialogActions>
      </Dialog>
    </ThemeProvider>
  );
};

export default LogInField;
