import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
// react-bootstrap
import Card from 'react-bootstrap/Card';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
// modal component
import AcceptModal from './acceptModal';
import RejectModal from './rejectModal';
// icons
import { FaRegCheckCircle, FaRegTimesCircle } from 'react-icons/fa';
// mui
import { IconButton, TextField, Autocomplete } from '@mui/material';
// import tables
import RawTable from './tablesComps/rawTable';
import ProcessedTableStatic from './tablesComps/processedTableStatic';
import HeatTableStatic from './tablesComps/heatTableStatic';
import LabTableStatic from './tablesComps/labTableStatic';
import ApiTable from './tablesComps/apiTable';

// import card
import QRInfoCard from './cardComps/QRInfoCard';
import MeatImgsCard from './cardComps/MeatImgsCard';
import MeatImgsCardStatic from './cardComps/MeatImgsCardStatic';

function DataConfirmView({ dataProps }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const pageOffset = searchParams.get('pageOffset');

  //1.dataProps로 부터 properties destruct
  const {
    id, // 이력번호
    userId, //로그인한 사용자 id
    createdAt, // 생성 시간
    qrImagePath, // qr 이미지 경로
    raw_img_path, // 원육 이미지 경로
    raw_data, // 원육 데이터
    processed_data, // 처리육 데이터
    heated_data, // 가열육 데이터
    lab_data, // 실험실 데이터
    api_data, // 축산물 이력 API 데이터
    processed_data_seq, // 처리 회차 {1회차, 2회차 ...}
    processed_minute, // 처리육 처리 시간
    processed_img_path, // 처리육 이미지 경로
  } = dataProps;

  //2.  <Autocomplete/> 컴포넌트의 option property값
  useEffect(() => {
    options = processed_data_seq;
  }, []);

  // 조회 선택한 처리육 데이터 회차 값
  const [processed_toggle, setProcessedToggle] = useState('1회');
  const [processedToggleValue, setProcessedToggleValue] = useState('');
  // 조회 선택한 가열육 데이터 회차 값
  const [heatedToggle, setHeatedToggle] = useState(options[0]);
  const [heatedToggleValue, setHeatedToggleValue] = useState('');
  // 조회 선택한 실험실 데이터 회차 값
  const [labToggle, setLabToggle] = useState(options[0]);
  const [labToggleValue, setLabToggleValue] = useState('');

  // 조회할 탭 값 설정
  const [value, setValue] = useState(0);
  // 탭 값 변경 시 value 설정
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  //3. 반려/승인 버튼 클릭에 따른 모달 창 컴포넌트 결정
  const [confirmVal, setConfirmVal] = useState(null);

  return (
    <div style={{ width: '100%', marginTop: '40px' }}>
      <div style={style.editBtnWrapper}>
        <IconButton
          style={style.acceptBtn}
          onClick={() => setConfirmVal('confirm')}
        >
          <FaRegCheckCircle />
          승인
        </IconButton>
        <IconButton
          style={style.rejectBtn}
          onClick={() => setConfirmVal('reject')}
        >
          <FaRegTimesCircle />
          반려
        </IconButton>
      </div>

      {
        // 승인 팝업 페이지
        confirmVal === 'confirm' && (
          <AcceptModal
            id={id}
            confirmVal={confirmVal}
            setConfirmVal={setConfirmVal}
          />
        )
      }
      {
        // 반려 팝업 페이지
        confirmVal === 'reject' && (
          <RejectModal
            id={id}
            confirmVal={confirmVal}
            setConfirmVal={setConfirmVal}
          />
        )
      }

      <div style={style.singleDataWrapper}>
        {/* 1. 관리번호 고기에 대한 사진*/}
        <MeatImgsCard
          edited={false}
          page={'검토'}
          raw_img_path={raw_img_path}
          processed_img_path={processed_img_path}
          id={id}
          raw_data={raw_data}
          butcheryYmd={api_data['butcheryYmd']}
          processed_data={processed_data}
          processedMinute={processed_minute}
        />
        {/* 2. QR코드와 데이터에 대한 기본 정보*/}
        <QRInfoCard
          qrImagePath={qrImagePath}
          id={id}
          userId={userId}
          createdAt={createdAt}
        />

        {/* 3. 세부 데이터 정보*/}
        <Card
          style={{
            width: '27vw',
            margin: '0px 10px',
            boxShadow: 24,
            height: '65vh',
          }}
        >
          <Tabs
            value={value}
            onChange={handleChange}
            defaultActiveKey="rawMeat"
            aria-label="tabs"
            className="mb-3"
            style={{ backgroundColor: 'white', width: '100%' }}
          >
            <Tab value="raw" eventKey="rawMeat" title="원육">
              <RawTable data={raw_data} />
            </Tab>

            <Tab
              value="proc"
              eventKey="processedMeat"
              title="처리육"
              style={{ backgroundColor: 'white' }}
            >
              <Autocomplete
                id={'controllable-states-processed'}
                label="처리상태"
                value={processed_toggle}
                onChange={(event, newValue) => {
                  setProcessedToggle(newValue);
                }}
                inputValue={processedToggleValue}
                onInputChange={(event, newInputValue) => {
                  setProcessedToggleValue(newInputValue); /*이미지 바꾸기 */
                }}
                options={options.slice(1)}
                size="small"
                sx={{ width: 'fit-content', marginBottom: '10px' }}
                renderInput={(params) => <TextField {...params} />}
              />
              <ProcessedTableStatic
                processedMinute={processed_minute}
                processed_data={processed_data}
                processedToggleValue={processedToggleValue}
              />
            </Tab>
            <Tab
              value="heat"
              eventKey="heatedMeat"
              title="가열육"
              style={{ backgroundColor: 'white' }}
            >
              <Autocomplete
                value={heatedToggle}
                size="small"
                onChange={(event, newValue) => {
                  setHeatedToggle(newValue);
                }}
                inputValue={heatedToggleValue}
                onInputChange={(event, newInputValue) => {
                  setHeatedToggleValue(newInputValue);
                }}
                id={'controllable-states-heated'}
                options={options}
                sx={{ width: 'fit-content', marginBottom: '10px' }}
                renderInput={(params) => (
                  <TextField {...params} label="처리상태" />
                )}
              />
              <HeatTableStatic
                heated_data={heated_data}
                heatedToggleValue={heatedToggleValue}
              />
            </Tab>
            <Tab
              value="lab"
              eventKey="labData"
              title="실험실"
              style={{ backgroundColor: 'white' }}
            >
              <Autocomplete
                value={labToggle}
                size="small"
                onChange={(event, newValue) => {
                  setLabToggle(newValue);
                }}
                inputValue={labToggleValue}
                onInputChange={(event, newInputValue) => {
                  setLabToggleValue(newInputValue);
                }}
                id={'controllable-states-api'}
                options={options}
                sx={{ width: 'fit-content', marginBottom: '10px' }}
                renderInput={(params) => (
                  <TextField {...params} label="처리상태" />
                )}
              />
              <LabTableStatic
                lab_data={lab_data}
                labToggleValue={labToggleValue}
              />
            </Tab>
            <Tab
              value="api"
              eventKey="api"
              title="축산물 이력"
              style={{ backgroundColor: 'white' }}
            >
              <ApiTable api_data={api_data} />
            </Tab>
          </Tabs>
        </Card>
      </div>
    </div>
  );
}

export default DataConfirmView;

// 토글 버튼
let options = ['원육'];

const style = {
  singleDataWrapper: {
    marginTop: '40px',
    display: 'flex',
    justifyContent: 'space-between',
  },
  editBtnWrapper: {
    paddingTop: '0px',
    width: '100%',
    display: 'flex',
    justifyContent: 'end',
    marginTop: 'auto',
    borderBottomLeftRadius: '10px',
    borderBottomRightRadius: '10px',
  },
  dataFieldColumn: {
    backgroundColor: '#9e9e9e',
    height: '33px',
    borderRight: '1px solid rgb(174, 168, 168)',
    borderBottom: '1px solid #fafafa',
    padding: '4px 5px',
  },
  dataExpColumn: {
    backgroundColor: '#757575',
    height: '33px',
    borderRight: '1px solid rgb(174, 168, 168)',
    borderBottom: '1px solid #fafafa',
    padding: '4px 5px',
    color: 'white',
  },
  dataFieldContainer: {
    backgroundColor: '#eeeeee',
    height: '100%',
    borderRight: '1px solid rgb(174, 168, 168)',
    borderBottom: '1px solid #fafafa',
    padding: '4px 5px',
  },
  dataContainer: {
    height: '33px',
    borderBottom: '0.8px solid #e0e0e0',
    width: '',
    borderRight: '0.8px solid #e0e0e0',
    padding: '4px 5px',
  },
  acceptBtn: {
    backgroundColor: '#00e676',
    color: 'white',
    fontSize: '15px',
    borderRadius: '5px',
    width: '80px',
    height: '35px',
  },
  rejectBtn: {
    backgroundColor: '#e53935',
    color: 'white',
    fontSize: '15px',
    borderRadius: '5px',
    width: '80px',
    height: '35px',
    marginLeft: '20px',
  },
};
