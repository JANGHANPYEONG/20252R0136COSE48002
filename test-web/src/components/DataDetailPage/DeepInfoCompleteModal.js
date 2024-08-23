import React from 'react';
import { Modal, Button } from 'react-bootstrap';

const navy = '#0F3659';

const DeepInfoCompleteModal = ({ show, onHide, meatId, seqno, type }) => {
  // type에 따라 다른 텍스트를 설정
  const getModalTitle = () => (type === 'add' ? '딥에이징 회차 추가' : '딥에이징 회차 삭제');
  const getModalMessage = () =>
    `${meatId} 데이터의 \n 딥에이징 ${seqno}회차가 ${type === 'add' ? '추가' : '삭제'}되었습니다.`;

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
            fontSize: '24px',
            fontWeight: 600,
          }}
        >
          {getModalTitle()}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body
        style={{
          textAlign: 'center',
          whiteSpace: 'pre-line',
          color: navy,
          fontSize: '18px',
          fontWeight: 600,
          width: '100%',
        }}
      >
        {getModalMessage()}
      </Modal.Body>
      <Modal.Footer style={{ border: 'none', justifyContent: 'center' }}>
        <Button
          onClick={onHide}
          style={{
            background: navy,
            width: '150px',
          }}
        >
          확인
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DeepInfoCompleteModal;
