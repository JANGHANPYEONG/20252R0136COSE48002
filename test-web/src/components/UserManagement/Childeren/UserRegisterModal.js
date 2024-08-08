import React, { useState } from 'react';
import Form from 'react-bootstrap/Form';
import { Button, Spinner, Modal } from 'react-bootstrap';
import InputGroup from 'react-bootstrap/InputGroup';
import { auth } from '../../../firebase-config';
import {
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
} from 'firebase/auth';
import { userRegister } from '../../../API/user/userRegister';
import { userDuplicateCheck } from '../../../API/user/userDuplicateCheck';
import RegisterCompletionModal from './RegisterCompletionModal';

const UserRegisterModal = ({ show, onHide }) => {
  const [userId, setuserId] = useState('');
  const [name, setname] = useState('');
  const [createdAt, setCreatedAt] = useState(
    new Date().toISOString().slice(0, -5)
  );
  const [updatedAt, setupdatedAt] = useState(
    new Date().toISOString().slice(0, -5)
  );
  const [loginAt, setloginAt] = useState(new Date().toISOString().slice(0, -5));
  const [password, setpassword] = useState('');
  const [company, setcompany] = useState('');
  const [jobTitle, setjobTitle] = useState('');
  const [homeAddr, sethomeAddr] = useState('');
  const [alarm, setalarm] = useState('');
  const [type, settype] = useState('');
  const [validated, setValidated] = useState(false);

  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const isEmailValid = (userId) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(userId);
  };

  const isNameValid = (name) => {
    const nameRegex = /^[가-힣a-zA-Z]+$/;
    return nameRegex.test(name);
  };

  const generateTempPassword = () => {
    const characters =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const length = 10;
    let tempPassword = '';
    for (let i = 0; i < length; i++) {
      tempPassword += characters.charAt(
        Math.floor(Math.random() * characters.length)
      );
    }
    return tempPassword;
  };

  const isFormValid = () => {
    return isEmailValid(userId) && isNameValid(name) && type !== '';
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (form.checkValidity() === false) {
      event.stopPropagation();
      setValidated(true);
      return;
    }

    if (isFormValid()) {
      setIsLoading(true);
      try {
        setCreatedAt(new Date().toISOString().slice(0, -5));
        const req = {
          userId: userId,
          name: name,
          company: company,
          jobTitle: jobTitle,
          homeAddr: homeAddr,
          alarm: alarm,
          type: type,
        };

        const registrationResponse = await userRegister(req);
        if (registrationResponse.ok) {
          const tempPassword = generateTempPassword();
          const { user } = await createUserWithEmailAndPassword(
            auth,
            userId,
            tempPassword
          );
          // await sendEmailVerification(user);
          await sendPasswordResetEmail(auth, userId);

          console.log('User registered successfully');
          setShowCompletionModal(true);
        } else {
          console.error('User registration failed');
          // 에러 처리를 위한 모달 또는 알림을 추가할 수 있습니다.
        }
      } catch (error) {
        console.error('Error during registration:', error);
        // 에러 처리를 위한 모달 또는 알림을 추가할 수 있습니다.
      } finally {
        setIsLoading(false);
      }
    }
    setValidated(true);
  };

  const [isEmailAvailable, setIsEmailAvailable] = useState(true);
  const [showifduplicate, setShowifduplicate] = useState(false);
  const handleDuplicateCheck = async () => {
    try {
      const response = await userDuplicateCheck(userId);
      const check = await response.json();
      if (!check.isDuplicated) {
        setIsEmailAvailable(true);
        console.log('OK');
      } else {
        setIsEmailAvailable(false);
        console.log('NO');
      }
    } catch (error) {
      setIsEmailAvailable(true);
      console.log('NO');
    }
    setShowifduplicate(true);
  };

  const handleCompletionModalClose = () => {
    setShowCompletionModal(false);
    onHide();
    window.location.reload();
  };
  // onHide
  return (
    <Modal
      show={show}
      onHide={onHide}
      backdrop="true"
      keyboard={false}
      centered
    >
      <Modal.Body>
        <Modal.Title
          style={{
            color: '#151D48',
            fontFamily: 'Poppins',
            fontSize: `24px`,
            fontWeight: 600,
          }}
        >
          신규 회원 등록
        </Modal.Title>
        <div>
          <div>
            <Form noValidate validated={validated} onSubmit={handleSubmit}>
              <Form.Label column>*아이디</Form.Label>
              <InputGroup className="mb-3" hasValidation>
                <Form.Control
                  required
                  type="email"
                  id="emailInput"
                  placeholder="이메일을 입력하세요"
                  onChange={(event) => {
                    setuserId(event.target.value);
                  }}
                />
                <Button
                  onClick={handleDuplicateCheck}
                  style={{
                    background: '#0F3659',
                  }}
                >
                  중복 확인
                </Button>
              </InputGroup>
              {showifduplicate && !isEmailAvailable && (
                <div className="text-danger">중복된 이메일입니다.</div>
              )}
              {showifduplicate && isEmailAvailable && (
                <div className="text-success">사용 가능한 이메일입니다.</div>
              )}

              <Form.Group className="mb-3">
                <Form.Label column>*이름</Form.Label>
                <Form.Control
                  required
                  type="text"
                  placeholder="이름을 입력하세요"
                  onChange={(event) => {
                    setname(event.target.value);
                  }}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Select
                  required
                  onChange={(event) => settype(event.target.value)}
                  aria-describedby="userSelectionFeedback"
                >
                  <option selected disabled value="">
                    *권한 선택
                  </option>
                  <option value="Normal">Normal</option>
                  <option value="Researcher">Researcher</option>
                </Form.Select>
                <Form.Control.Feedback type="invalid">
                  권한을 선택하세요.
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label column>소속</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="회사명 입력"
                  onChange={(event) => {
                    setcompany(event.target.value);
                  }}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Control
                  type="text"
                  placeholder="직책 입력"
                  onChange={(event) => {
                    setjobTitle(event.target.value);
                  }}
                />
              </Form.Group>

              <Form.Group className="mb-3" controlId="formGridAddress1">
                <Form.Control
                  type="text"
                  placeholder="회사주소"
                  onChange={(event) => {
                    sethomeAddr(event.target.value);
                  }}
                />
              </Form.Group>

              <div className="text-end">
                <Button variant="text" onClick={onHide}>
                  취소
                </Button>
                <Button
                  type="submit"
                  onClick={handleSubmit}
                  style={{
                    background: '#0F3659',
                    width: '150px',
                  }}
                  disabled={!isFormValid() || !isEmailAvailable || isLoading}
                >
                  {isLoading ? (
                    <Spinner animation="border" size="sm" />
                  ) : (
                    '회원 등록'
                  )}
                </Button>
              </div>
            </Form>
          </div>
          {showCompletionModal && (
            <div
              className="modal-backdrop"
              style={{
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                zIndex: 1040,
              }}
            />
          )}
          <RegisterCompletionModal
            show={showCompletionModal}
            onHide={handleCompletionModalClose}
          />
        </div>
      </Modal.Body>
    </Modal>
  );
};
export default UserRegisterModal;
