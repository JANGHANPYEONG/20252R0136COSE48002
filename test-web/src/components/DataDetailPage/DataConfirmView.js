import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
// react-bootstrap
import Card from 'react-bootstrap/Card';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
// userContext
import { useUser } from '../../Utils/UserContext';
// modal component
import InputTransitionsModal from './InputTransitionsModal';
// mui
// import { TextField, Autocomplete } from '@mui/material';
// import tables
import RawTable from './TablesComps/RawTable';
import ProcessedTable from './TablesComps/ProcessedTable';
import HeatTable from './TablesComps/HeatTable';
import LabTable from './TablesComps/LabTable';
import ApiTable from './TablesComps/ApiTable';
// import timezone
import { TIME_ZONE } from '../../config';
import Spinner from 'react-bootstrap/Spinner';
// import update APIs
import addHeatedData from '../../API/add/addHeatedData';
import addProbexptData from '../../API/add/addProbexptData';
import addSensoryProcessedData from '../../API/add/addSensoryProcessedData';
import addSensoryRawData from '../../API/add/addSensoryRawData';
import RestrictedModal from './RestrictedModal';
// import card
import QRInfoCard from './CardComps/QRInfoCard';
import MeatImgsCard from './CardComps/MeatImgsCard';
import { computePeriod } from './computeTime';

// modal component
import AcceptModal from './AcceptModal';
import RejectModal from './RejectModal';
// icons
import { FaRegCheckCircle, FaRegTimesCircle } from 'react-icons/fa';
// mui
import { IconButton, TextField, Autocomplete } from '@mui/material';
import { style, divStyle } from './style/dataviewstyle';

// import tables
// import RawTable from './tablesComps/rawTable';
import ProcessedTableStatic from './TablesComps/ProcessedTableStatic';
import HeatTableStatic from './TablesComps/HeatTableStatic';
import LabTableStatic from './TablesComps/LabTableStatic';
// import ApiTable from './tablesComps/apiTable';

// import card
// import QRInfoCard from './cardComps/QRInfoCard';
// import MeatImgsCard from './cardComps/MeatImgsCard';
import MeatImgsCardStatic from './CardComps/MeatImgsCardStatic';

const navy = '#0F3659';

const DataView = ({ dataProps }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const pageOffset = searchParams.get('pageOffset');

  //dataProps로 부터 properties destruct
  const {
    meatId, // 이력번호
    userId, // 로그인한 사용자
    createdAt, // 생성 시간
    qrImagePath, // QR이미지 경로
    raw_img_path, // 원육 이미지 경로
    raw_data, // 원육 데이터
    processed_data, // 처리육 데이터
    heated_data, // 가열육 데이터
    lab_data, // 실험실 데이터
    api_data, // 축산물 이력 API 데이터
    processed_data_seq, // 처리(딥에이징) 회차
    processed_minute, // 처리 시간(분)
    processed_img_path, // 처리육 이미지 경로
  } = dataProps;

  const [processedMinute, setProcessedMinute] = useState(processed_minute);
  //탭 정보
  const tabFields = [rawField, deepAgingField, heatedField, labField, apiField];
  // 탭별 데이터 -> datas는 불변 , input text를 바꾸고 서버에 전송
  const datas = [raw_data, processed_data, heated_data, lab_data, api_data];

  useEffect(() => {
    options = processed_data_seq;
  }, []);

  // 처리육 및 실험 회차 토글
  const [processed_toggle, setProcessedToggle] = useState('1회');
  const [processedToggleValue, setProcessedToggleValue] = useState('');
  const [heatedToggle, setHeatedToggle] = useState(options[0]);
  const [heatedToggleValue, setHeatedToggleValue] = useState('');
  const [labToggle, setLabToggle] = useState(options[0]);
  const [labToggleValue, setLabToggleValue] = useState('');

  // "원육","처리육","가열육","실험실+전자혀","축산물 이력",별 수정 및 추가 input text
  const [rawInput, setRawInput] = useState({});
  const [processedInput, setProcessedInput] = useState({});
  const [heatInput, setHeatInput] = useState({});
  const [labInput, setLabInput] = useState({});
  const [apiInput, setApiInput] = useState(api_data);
  // setInputFields를 통해 인덱스 값으로 수정할 Field를 접근
  const setInputFields = [
    { value: rawInput, setter: setRawInput },
    { value: processedInput, setter: setProcessedInput },
    { value: heatInput, setter: setHeatInput },
    { value: labInput, setter: setLabInput },
    { value: apiInput, setter: setApiInput },
  ];

  // input field별 value prop으로 만들기
  useEffect(() => {
    tabFields.map((t, index) => {
      if (datas[index] === null || datas[index].length === 0) {
        // 데이터가 없는 경우 ""값으로
        t.forEach((f) => {
          setInputFields[index].setter((currentField) => ({
            ...currentField,
            [f]: '',
          }));
        });
      } else {
        setInputFields[index].setter(datas[index]);
      }
    });
  }, []);

  // 수정 여부 버튼 토글
  const [edited, setIsEdited] = useState(false);
  // 수정 버튼 클릭 시, input field로 전환
  const onClickEditBtn = () => {
    setIsEdited(true);
  };

  const len = processed_data_seq.length;

  const [isLimitedToChangeImage, setIsLimitedToChangeImage] = useState(false);
  // UserContext에서 유저 정보 불러오기
  const user = useUser();
  // 수정 완료 버튼 클릭 시 ,수정된 data api로 전송
  const onClickSubmitBtn = async () => {
    setIsEdited(false);
    // 수정 시간
    const createdDate = new Date(new Date().getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);
    // period 계산
    const elapsedHour = computePeriod(apiInput['butcheryYmd']);
    //로그인한 유저 정보
    const userId = user.userId;

    //4. 원육 데이터 수정 API
    addSensoryRawData(rawInput, 0, meatId)
      .then((response) => {
        console.log('원육 수정 POST요청 성공:', response);
      })
      .catch((error) => {
        // 오류 발생 시의 처리
        console.error('원육 수정 POST 요청 오류:', error);
      });
  };

  // 처리육 이미지 먼저 업로드 경고 창 필요 여부
  const [modal, setModal] = useState(false);

  // input 변화 감지 함수
  const handleInputChange = (e, idx, valueIdx) => {
    // e : event 객체, idx : setInputFields의 인덱스, valueIdx : 수정한 input의 딥에이징 회차 (0:원육, 1~n: n회차 처리육)
    // input 변화 값
    const value = e.target.value;

    // idx === 1은 processedInput field임을 의미
    if (idx === 1) {
      // 해당 딥에에징 회차의 이미지가 입력되어있지 않으면 경고 창 띄우기
      if (imgArr[valueIdx + 1] === null || imgArr[valueIdx + 1] === undefined) {
        console.log('처리육 이미지를 먼저 업로드 하세요!');
        setModal(true);
        return <InputTransitionsModal setModal={setModal} />;
      }
    }

    // input 변화가 생기면 수정한 값으로 업데이트
    let temp = setInputFields[idx].value[valueIdx];
    if (!isNaN(+value)) {
      temp = { ...temp, [e.target.name]: value };
      setInputFields[idx].setter((currentField) => ({
        ...currentField,
        [valueIdx]: temp,
      }));
      console.log('result', temp, valueIdx);
    }
  };
  const handleRawInputChange = (e, field) => {
    const { name, value } = e.target;
    setRawInput((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const [imgArr, setImgArr] = useState([raw_img_path]);
  useEffect(() => {
    processed_img_path.length !== 0
      ? //{}이 아닌 경우
        setImgArr([...imgArr, ...processed_img_path])
      : //{}인 경우 -> 1회차 처리육 정보 입력을 위해 null 생성
        setImgArr([...imgArr, null]);
  }, []);

  // "원육","처리육","가열육","실험실","축산물 이력" 탭 값 설정
  const [value, setValue] = useState(0);
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  //3. 반려/승인 버튼 클릭에 따른 모달 창 컴포넌트 결정
  const [confirmVal, setConfirmVal] = useState(null);

  // 이미지 파일 변경 완료 여부
  const [isUploadingDone, setIsUploadingDone] = useState(true);

  return (
    <div style={{ width: '100%', marginTop: '40px' }}>
      {!isUploadingDone && (
        <div style={divStyle.loadingBackground}>
          <Spinner />
          <span style={divStyle.loadingText}>이미지를 업로드 중 입니다..</span>
        </div>
      )}
      {user.type === 'Manager' && (
        <div style={style.confirmEditBtnWrapper}>
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
      )}

      {
        // 승인 팝업 페이지
        confirmVal === 'confirm' && (
          <AcceptModal
            meatId={meatId}
            confirmVal={confirmVal}
            setConfirmVal={setConfirmVal}
          />
        )
      }
      {
        // 반려 팝업 페이지
        confirmVal === 'reject' && (
          <RejectModal
            meatId={meatId}
            confirmVal={confirmVal}
            setConfirmVal={setConfirmVal}
          />
        )
      }
      {
        // 이미지 수정 불가능 팝업 - 일반 사용자임을 알리거나 서버를 확인하라는 경고 메시지
        isLimitedToChangeImage && (
          <RestrictedModal
            setIsLimitedToChangeImage={setIsLimitedToChangeImage}
          />
        )
      }
      <div style={style.singleDataWrapper}>
        {/* 1. 관리번호 육류에 대한 사진*/}
        <MeatImgsCard
          edited={edited}
          page={'수정및조회'}
          raw_img_path={raw_img_path}
          processed_img_path={processed_img_path}
          setIsUploadingDone={setIsUploadingDone}
          id={meatId}
          raw_data={raw_data}
          setIsLimitedToChangeImage={setIsLimitedToChangeImage}
          butcheryYmd={api_data['butcheryYmd']}
          processedInput={processedInput}
          processed_data={processed_data}
          processedMinute={processedMinute}
          processed_data_seq={processed_data_seq}
        />
        {/* 2. QR코드와 데이터에 대한 기본 정보*/}
        <QRInfoCard
          qrImagePath={qrImagePath}
          id={meatId}
          userId={userId}
          createdAt={createdAt}
        />
        {/* 3. 세부 데이터 정보*/}
        <Card
          style={{
            width: '27vw',
            margin: '0px 10px',
            boxShadow: 24,
            minWidth: '360px',
            height: '65vh',
            minHeight: '500px',
            // display: 'flex',
            // flexDirection: 'column',
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
              <RawTable
                data={rawInput}
                edited={edited}
                handleRawInputChange={handleRawInputChange}
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
      <div style={style.editBtnWrapper}>
        {edited ? (
          <button
            type="button"
            style={style.completeBtn}
            onClick={onClickSubmitBtn}
          >
            완료
          </button>
        ) : (
          <button type="button" style={style.editBtn} onClick={onClickEditBtn}>
            수정
          </button>
        )}
      </div>
    </div>
  );
};

export default DataView;

// 토글 버튼
let options = ['원육'];

const rawField = ['marbling', 'color', 'texture', 'surfaceMoisture', 'overall'];
const deepAgingField = [
  'marbling',
  'color',
  'texture',
  'surfaceMoisture',
  'overall',
  'createdAt',
  'seqno',
  'minute',
  'period',
];
const heatedField = [
  'flavor',
  'juiciness',
  'tenderness',
  'umami',
  'palatability',
];
const labField = [
  'L',
  'a',
  'b',
  'DL',
  'CL',
  'RW',
  'ph',
  'WBSF',
  'cardepsin_activity',
  'MFI',
  'sourness',
  'bitterness',
  'umami',
  'richness',
  'Collagen',
];
const apiField = [
  'birthYmd',
  'butcheryYmd',
  'farmAddr',
  'farmerName',
  'gradeNm',
  'primalValue',
  'secondaryValue',
  'sexType',
  'species',
  'statusType',
  'traceNum',
];
