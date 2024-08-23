/* 유저 등록 모달 */
/* 유저 등록 및 등록완료확인 모달 표시 처리 */
import React, { useState, useEffect } from 'react';
import Form from 'react-bootstrap/Form';
import { Button, Spinner, Modal } from 'react-bootstrap';
import InputGroup from 'react-bootstrap/InputGroup';
import { userDuplicateCheck } from '../../../API/user/userDuplicateCheck';
import handleUserRegisterSubmit from './UserRegisterModalChildren/handleUserRegisterSubmit';
import RegisterCompletionModal from './UserRegisterModalChildren/RegisterCompletionModal';

const UserRegisterModal = ({ show, onHide }) => {
  const [userId, setUserId] = useState('');
  const [name, setName] = useState('');
  // const [createdAt, setCreatedAt] = useState(
  //   new Date().toISOString().slice(0, -5)
  // );
  // const [updatedAt, setUpdatedAt] = useState(
  //   new Date().toISOString().slice(0, -5)
  // );
  // const [loginAt, setLoginAt] = useState(new Date().toISOString().slice(0, -5));
  // const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [homeAddr, setHomeAddr] = useState('');
  const [alarm, setAlarm] = useState('');
  const [type, setType] = useState('');

  const [validated, setValidated] = useState(false);
  const [isEmailAvailable, setIsEmailAvailable] = useState(true);
  const [showIfDuplicate, setShowIfDuplicate] = useState(false);

  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!show) {
      resetForm();
    }
  }, [show]);

  const resetForm = () => {
    setUserId('');
    setName('');
    setCompany('');
    setJobTitle('');
    setHomeAddr('');
    setAlarm('');
    setType('');
    setValidated(false);
    setIsEmailAvailable(true);
    setShowIfDuplicate(false);
  };

  const isEmailValid = (userId) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(userId);
  };

  const isNameValid = (name) => {
    const nameRegex = /^[가-힣a-zA-Z]+$/;
    return nameRegex.test(name);
  };

  const isFormValid = () => {
    return isEmailValid(userId) && isNameValid(name) && type !== '';
  };

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
    setShowIfDuplicate(true);
  };

  const handleCompletionModalClose = () => {
    setShowCompletionModal(false);
    onHide();
    window.location.reload();
  };

  const submitData = {
    event: null,
    setValidated,
    isFormValid,
    setIsLoading,
    // setCreatedAt,
    userId,
    name,
    company,
    jobTitle,
    homeAddr,
    alarm,
    type,
    setShowCompletionModal,
  };

  return (
    <Modal
      show={show}
      onHide={isLoading ? null : onHide}
      backdrop={isLoading ? 'static' : true}
      keyboard={!isLoading}
      centered
    >
      <Modal.Body>
        <Modal.Title
          style={{
            color: '#151D48',
            fontFamily: 'Poppins',
            fontSize: '24px',
            fontWeight: 600,
          }}
        >
          신규 회원 등록
        </Modal.Title>
        <div>
          <Form
            noValidate
            validated={validated}
            onSubmit={(event) => {
              submitData.event = event;
              handleUserRegisterSubmit(submitData);
            }}
          >
            <Form.Label column>*아이디</Form.Label>
            <InputGroup className="mb-3" hasValidation>
              <Form.Control
                required
                type="email"
                id="emailInput"
                placeholder="이메일을 입력하세요"
                onChange={(event) => setUserId(event.target.value)}
              />
              <Button
                onClick={handleDuplicateCheck}
                style={{ background: '#0F3659' }}
              >
                중복 확인
              </Button>
            </InputGroup>
            {showIfDuplicate && !isEmailAvailable && (
              <div className="text-danger">중복된 이메일입니다.</div>
            )}
            {showIfDuplicate && isEmailAvailable && (
              <div className="text-success">사용 가능한 이메일입니다.</div>
            )}

            <Form.Group className="mb-3">
              <Form.Label column>*이름</Form.Label>
              <Form.Control
                required
                type="text"
                placeholder="이름을 입력하세요"
                onChange={(event) => setName(event.target.value)}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Select
                required
                onChange={(event) => setType(event.target.value)}
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
                onChange={(event) => setCompany(event.target.value)}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Control
                type="text"
                placeholder="직책 입력"
                onChange={(event) => setJobTitle(event.target.value)}
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formGridAddress1">
              <Form.Control
                type="text"
                placeholder="회사주소"
                onChange={(event) => setHomeAddr(event.target.value)}
              />
            </Form.Group>

            <div className="text-end">
              <Button variant="text" onClick={onHide}>
                취소
              </Button>
              <Button
                type="submit"
                style={{ background: '#0F3659', width: '150px' }}
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
