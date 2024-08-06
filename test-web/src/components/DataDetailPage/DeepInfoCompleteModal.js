import React from 'react';
import { Modal, Button } from 'react-bootstrap';

const navy = '#0F3659';

const DeepInfoCompletionModal = ({ show, onHide, meatId, maxSeqno }) => {
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
          딥에이징 회차 추가
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
          `${meatId} 데이터의 \n 딥에이징 ${maxSeqno}회차가 추가되었습니다.`
        }
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

export default DeepInfoCompletionModal;
