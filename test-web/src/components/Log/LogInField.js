import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from 'firebase/auth';
import { auth } from '../../firebase-config';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Typography from '@mui/material/Typography';
import Layer_1 from '../../src_assets/Layer_1.png';
import BackGround from '../../src_assets/BackGround.png';
import { apiIP } from '../../config';

const defaultTheme = createTheme();
const LogInField = () => {
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [rememberMe, setRememberMe] = useState(false); // New state variable for "Remember Me" checkbox

  useEffect(() => {
    // Check if the email was stored in the local storage
    const storedEmail = localStorage.getItem('rememberedEmail');
    if (storedEmail) {
      setLoginEmail(storedEmail);
      setRememberMe(true);
    }
  }, []);

  const register = async () => {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        registerEmail,
        registerPassword
      );
      console.log(userCredential.user);
    } catch (error) {
      console.log(error.message);
    }
  };

  const navigate = useNavigate();
  const login = async () => {
    try {
      if (!loginEmail) {
        setLoginError('아이디를 입력해주세요.');
        return;
      }
      if (!loginPassword) {
        setLoginError('비밀번호를 입력해주세요.');
        return;
      }
      const auth = getAuth();
      const response = await fetch(
        `http://${apiIP}/user/login?userId=${loginEmail}`
      );
      const user = await response.json();
      if (user.type === 'Normal') {
        //아이디는 존재하지만 관리자가 아니라면
        setLoginError('로그인 권한이 없습니다. 관리자에게 문의해주세요.');
        return;
      }

      try {
        await signInWithEmailAndPassword(auth, loginEmail, loginPassword);
      } catch (error) {
        if (error.code === 'auth/user-not-found') {
          //아이디가 존재하지 않는다면
          setLoginError('존재하지 않는 아이디입니다.');
          return;
        } else if (user.type === 'Normal') {
          //아이디는 존재하지만 관리자가 아니라면
          setLoginError('로그인 권한이 없습니다. 관리자에게 문의해주세요.');
          return;
        } else if (error.code === 'auth/too-many-requests') {
          //로그인을 너무 많이 시도하면
          setLoginError(
            '로그인을 너무 많이 시도했습니다. 잠시후 다시 시도해주세요.'
          );
          return;
        } else {
          // 비밀번호가 일치하지 않는다면
          setLoginError('비밀번호가 일치하지 않습니다.');
          return;
        }
      }
      if (rememberMe) {
        localStorage.setItem('rememberedEmail', loginEmail);
      } else {
        localStorage.removeItem('rememberedEmail');
      }
      //로그인 성공 시 홈으로 이동
      const userCredential = await signInWithEmailAndPassword(
        auth,
        loginEmail,
        loginPassword
      );
      localStorage.setItem('UserInfo', JSON.stringify(user));
      const updateinfo = JSON.parse(localStorage.getItem('updateinfo'));

      localStorage.setItem('isLoggedIn', 'true');
      console.log('LOGIN SUCCESS');
      navigate('/Home');
      window.location.reload();
    } catch (error) {
      console.log(error.message);
      setLoginError('로그인에 실패했습니다. 다시 시도해주세요.');
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      if (event.target.name === 'email') {
        // 아이디 필드에서 Enter 키를 누르면 비밀번호 필드로 이동
        document.getElementById('password').focus();
      } else if (event.target.name === 'password') {
        // 비밀번호 필드에서 Enter 키를 누르면 로그인 버튼 클릭
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
          minWidth: '100vw', // 전체 화면 너비
          backgroundImage: `url(${BackGround})`, // 경로를 실제 파일 경로로 변경
          backgroundSize: 'cover', // 배경 이미지 크기 조절 (cover는 화면 전체를 채우도록 설정)
          backgroundRepeat: 'no-repeat', // 배경 이미지 반복 방지
        }}
      >
        <CssBaseline />
        <img
          src={Layer_1}
          style={{
            width: `${(323 / 1920) * 100}vw`,
            marginBottom: `${(48 / 1080) * 100}vh`,
            marginTop: `${(200 / 1080) * 100}vh`,
          }}
        />

        <Box
          component="form"
          noValidate
          sx={{
            flexDirection: 'column', // 세로로 배치
            justifyContent: 'center',
            width: `${(450 / 1920) * 100}vw`, // 너비를 450px로 설정
            height: `${(594 / 1080) * 100}vh`,
            bgcolor: 'white',
            paddingX: `${(42 / 1920) * 100}vw`, // 가로 패딩
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
            onChange={(event) => {
              setLoginEmail(event.target.value);
            }}
            onKeyPress={handleKeyPress}
            style={{
              width: `${(365 / 1920) * 100}vw`, // 너비를 365px로 설정
              height: `${(72 / 1080) * 100}vh`, // 높이를 72px로 설정
              padding: '8px', // Add padding for styling if needed
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
            onChange={(event) => {
              setLoginPassword(event.target.value);
            }}
            onKeyPress={handleKeyPress}
            style={{
              width: `${(365 / 1920) * 100}vw`, // 너비를 365px로 설정
              height: `${(72 / 1080) * 100}vh`, // 높이를 72px로 설정
              padding: '8px', // Add padding for styling if needed
            }}
          />
          <FormControlLabel
            control={
              <Checkbox
                value={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
                color="primary"
                checked={rememberMe}
              />
            }
            label="아이디 저장"
          />
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
    </ThemeProvider>
  );
};

export default LogInField;
