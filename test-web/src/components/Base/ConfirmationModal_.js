import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

function ConfirmationModal({ show, onClose, onConfirm }) {
  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>변경하시겠습니까?</Modal.Title>
      </Modal.Header>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => onConfirm(false)}>
          아니오
        </Button>
        <Button variant="primary" onClick={() => onConfirm(true)}>
          네
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
