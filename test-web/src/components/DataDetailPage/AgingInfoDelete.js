import { Button } from 'react-bootstrap';
import Spinner from 'react-bootstrap/Spinner';
import { useState } from 'react';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import DeepInfoCompleteModal from './DeepInfoCompleteModal';
import deleteDeepAging from '../../API/delete/deleteDeepAging';

const AgingInfoDeleter = ({ handleClose, meatId, processed_data_seq }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [validated, setValidated] = useState(false);
  const [seqno, setSeqno] = useState('');
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
      const Response = await deleteDeepAging(meatId, seqno);
      if (Response.ok) {
        console.log('Success to delete DeepInfo');
        setShowCompletionModal(true);
      }
    } catch (error) {
      console.error('Error during deletion', error);
    } finally {
      setIsLoading(false);
    }

    setValidated(true);
  };

  const filteredSeqs = processed_data_seq.filter((seq) => seq !== '원육');
  return (
    <div>
      <div>
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Label column></Form.Label>
          <InputGroup className="mb-3" hasValidation>
            <Form.Select
              required
              id="SelectSeqno"
              onChange={(event) => {
                const selectedSeq = filteredSeqs[event.target.value].replace('회', '');
                setSeqno(selectedSeq);
              }}
              //value={seqno}
              defaultValue=""
            >
              <option value="" disabled hidden>
                삭제할 회차를 선택하세요
              </option>
              {filteredSeqs.map((item, index) => (
                <option key={index} value={index}>
                  {item}
                </option>
              ))}
            </Form.Select>
          </InputGroup>

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
              disabled={isLoading || !seqno}
            >
              {isLoading ? (
                <Spinner animation="border" size="sm" />
              ) : (
                '회차 삭제'
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
      <DeepInfoCompleteModal
        show={showCompletionModal}
        onHide={handleCompletionModalClose}
        meatId={meatId}
        seqno={seqno}
        type = "delete"
      />
    </div>
  );
};
export default AgingInfoDeleter;
