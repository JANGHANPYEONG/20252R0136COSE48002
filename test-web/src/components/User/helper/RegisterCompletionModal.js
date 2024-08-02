import React from 'react';
import { Modal, Button } from 'react-bootstrap';

const navy = '#0F3659';

function RegisterCompletionModal({ show, onHide }) {
  return (
    <Modal
      show={show}
      onHide={onHide}
      backdrop={false}
      keyboard={false}
      centered
      size="sm"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
      }}
    >
      <Modal.Header style={{ border: 'none' }}>
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
      </Modal.Header>
      <Modal.Body
        style={{
          textAlign: 'center',
          whiteSpace: 'pre-line',
          color: navy,
          fontSize: '18px',
          fontWeight: '600',
          width: '100%',
        }}
      >
        {
          '회원 등록이 완료되었습니다.\n비밀번호 설정을 위해\n이메일을 확인해 주세요.'
        }
      </Modal.Body>
      <Modal.Footer style={{ border: 'none', justifyContent: 'center' }}>
        <Button
          onClick={onHide}
          style={{
            background: '#0F3659',
            width: '150px',
          }}
        >
          확인
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default RegisterCompletionModal;
