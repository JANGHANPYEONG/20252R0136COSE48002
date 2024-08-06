import { Button } from 'react-bootstrap';
import Spinner from 'react-bootstrap/Spinner';
import { useState } from 'react';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import addDeepAgingRegister from '../../API/add/addDeepAging';
import DeepInfoCompletionModal from './DeepInfoCompleteModal';

const AgingInfoRegister = ({ handleClose, maxSeqno, meatId }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [validated, setValidated] = useState(false);
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [showCompletionModal, setShowCompletionModal] = useState(false);

  const handleCompletionModalClose = () => {
    setShowCompletionModal(false);
    handleClose();
    window.location.reload();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (form.checkValidity() === false) {
      event.stopPropagation();
      setValidated(true);
      return;
    }

    setIsLoading(true);
    try {
      const req = {
        meatId: meatId,
        seqno: maxSeqno,
        deepAging: {
          date: date,
          minute: time,
        },
      };
      const registerResponse = await addDeepAgingRegister(req);
      if (registerResponse.ok) {
        console.log('Success to register DeepInfo');
        setShowCompletionModal(true);
      }
    } catch (error) {
      console.error('Error during registration', error);
    } finally {
      setIsLoading(false);
    }

    setValidated(true);
  };
  return (
    <div>
      <div>
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Label column>*Date</Form.Label>
          <InputGroup className="mb-3" hasValidation>
            <Form.Control
              required
              type="Date"
              id="DateInput"
              placeholder="날짜를 입력하세요"
              onChange={(event) => {
                setDate(event.target.value);
              }}
            />
          </InputGroup>
          <Form.Group className="mb-3">
            <Form.Label column>시간(분)</Form.Label>
            <Form.Control
              required
              type="number"
              placeholder="딥에이징 시간(분)"
              onChange={(event) => {
                setTime(event.target.value);
              }}
            />
          </Form.Group>

          <div className="text-end">
            <Button variant="text" onClick={handleClose}>
              취소
            </Button>
            <Button
              type="submit"
              onClick={handleSubmit}
              style={{
                background: '#0F3659',
                width: '150px',
              }}
              disabled={isLoading || !date || !time}
            >
              {isLoading ? (
                <Spinner animation="border" size="sm" />
              ) : (
                '회차 등록'
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
      <DeepInfoCompletionModal
        show={showCompletionModal}
        onHide={handleCompletionModalClose}
        meatId={meatId}
        maxSeqno={maxSeqno}
      />
    </div>
  );
};
export default AgingInfoRegister;
