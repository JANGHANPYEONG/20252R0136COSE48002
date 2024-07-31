import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
// react-bootstrap
import Card from 'react-bootstrap/Card';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
// modal component
import InputTransitionsModal from './InputWarningComp';
// mui
import { TextField, Autocomplete } from '@mui/material';
// import tables
import RawTable from './tablesComps/rawTable';
import ProcessedTable from './tablesComps/processedTable';
import HeatTable from './tablesComps/heatTable';
import LabTable from './tablesComps/labTable';
import ApiTable from './tablesComps/apiTable';
// import timezone
import { TIME_ZONE } from '../../config';
import Spinner from 'react-bootstrap/Spinner';
// import update APIs
import addHeatedData from '../../API/add/addHeatedData';
import addProbexptData from '../../API/add/addProbexptData';
import addSensoryProcessedData from '../../API/add/addSensoryProcessedData';
import RestrictedModal from './restrictedModal';
// import card
import QRInfoCard from './cardComps/QRInfoCard';
import MeatImgsCard from './cardComps/MeatImgsCard';
import { computePeriod } from './computePeriod';
import isPost from '../../API/isPost';

const navy = '#0F3659';

function DataView({ dataProps }) {
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

  // console.log(`1회차 가열육 데이터: ${JSON.stringify(heated_data[1])}`);
  // console.log(`1회차 처리육 데이터: ${JSON.stringify(processed_data[0])}`);
  // console.log(`1회차 실험육 데이터: ${JSON.stringify(lab_data[1])}`);

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
  const [processedToggleValue, setProcessedToggleValue] = useState('1회');
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

  const [isProcessedPosted, setIsProcessedPosted] = useState({});
  const [isLabPosted, setIsLabPosted] = useState({});
  const [isHeatedPosted, setIsHeatedPosted] = useState({});

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

  // 수정 완료 버튼 클릭 시 수정된 data API로 전송
  const onClickSubmitBtn = async () => {
    setIsEdited(false);
    // 수정 시간
    const createdDate = new Date(new Date().getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);
    // period 계산
    const elapsedHour = computePeriod(apiInput['butcheryYmd']);
    //로그인한 유저 정보
    const currentUserId = JSON.parse(localStorage.getItem('UserInfo'))[
      'userId'
    ];

    // 1. 가열육 관능검사 데이터 생성/수정 API POST/PATCH
    let dict = {};
    for (let i = 0; i < len; i++) {
      const isMethodPost = await isPost(
        [
          heated_data[i]?.flavor,
          heated_data[i]?.juiciness,
          heated_data[i]?.palatability,
          heated_data[i]?.tenderness,
          heated_data[i]?.umami,
        ],
        [
          heatInput[i]?.flavor,
          heatInput[i]?.juiciness,
          heatInput[i]?.palatability,
          heatInput[i]?.tenderness,
          heatInput[i]?.umami,
        ],
        isHeatedPosted[i]
      );
      if (isMethodPost === undefined) continue;
      else if (isMethodPost) dict = { ...dict, [i]: isMethodPost };

      addHeatedData(heatInput[i], i, meatId, currentUserId, isMethodPost)
        .then((response) => {
          if (response.ok)
            console.log(
              `가열육 ${isMethodPost ? '생성 POST' : '수정 PATCH'} 요청 성공`,
              response.msg
            );
        })
        .catch((error) => {
          console.error(
            `가열육 ${isMethodPost ? '생성 POST' : '수정 PATCH'} 요청 오류`,
            error
          );
        });
    }
    setIsHeatedPosted({ ...isHeatedPosted, ...dict });

    // 2. 실험실 데이터 생성/수정 API POST/PATCH
    dict = {};
    for (let i = 0; i < len; i++) {
      const isMethodPost = await isPost(
        [
          lab_data[i]?.L,
          lab_data[i]?.a,
          lab_data[i]?.b,
          lab_data[i]?.DL,
          lab_data[i]?.CL,
          lab_data[i]?.RW,
          lab_data[i]?.ph,
          lab_data[i]?.WBSF,
          lab_data[i]?.cardepsin_activity,
          lab_data[i]?.MFI,
          lab_data[i]?.Collagen,
          lab_data[i]?.sourness,
          lab_data[i]?.bitterness,
          lab_data[i]?.umami,
          lab_data[i]?.richness,
        ],
        [
          labInput[i]?.L,
          labInput[i]?.a,
          labInput[i]?.b,
          labInput[i]?.DL,
          labInput[i]?.CL,
          labInput[i]?.RW,
          labInput[i]?.ph,
          labInput[i]?.WBSF,
          labInput[i]?.cardepsin_activity,
          labInput[i]?.MFI,
          labInput[i]?.Collagen,
          labInput[i]?.sourness,
          labInput[i]?.bitterness,
          labInput[i]?.umami,
          labInput[i]?.richness,
        ],
        isLabPosted[i]
      );
      if (isMethodPost === undefined) continue;
      else if (isMethodPost) dict = { ...dict, [i]: isMethodPost };
      addProbexptData(labInput[i], i, meatId, currentUserId, isMethodPost)
        .then((response) => {
          if (response.ok)
            console.log(
              `실험실 ${isMethodPost ? '생성 POST' : '수정 PATCH'} 요청 성공`,
              response.msg
            );
        })
        .catch((error) => {
          console.error(
            `실험실 ${isMethodPost ? '생성 POST' : '수정 PATCH'} 요청 오류`,
            error
          );
        });
    }
    setIsLabPosted({ ...isLabPosted, ...dict });

    // 3. 처리육 관능검사 데이터 생성/수정 API POST/PATCH
    dict = {};
    const pro_len = len === 1 ? len : len - 1;
    for (let i = 0; i < pro_len; i++) {
      const isMethodPost = await isPost(
        [
          processed_data[i]?.marbling,
          processed_data[i]?.color,
          processed_data[i]?.texture,
          processed_data[i]?.surfaceMoisture,
          processed_data[i]?.overall,
        ],
        [
          processedInput[i]?.marbling,
          processedInput[i]?.color,
          processedInput[i]?.texture,
          processedInput[i]?.surfaceMoisture,
          processedInput[i]?.overall,
        ],
        isProcessedPosted[i + 1]
      );
      if (isMethodPost === undefined) continue;
      else if (isMethodPost) dict = { ...dict, [i + 1]: isMethodPost };
      addSensoryProcessedData(
        processedInput[i],
        i,
        meatId,
        currentUserId,
        isMethodPost
      )
        .then((response) => {
          if (response.ok)
            console.log(
              `처리육 ${isMethodPost ? '생성 POST' : '수정 PATCH'} 요청 성공`,
              response.msg
            );
        })
        .catch((error) => {
          console.error(
            `처리육 ${isMethodPost ? '생성 POST' : '수정 PATCH'} 요청 오류`,
            error
          );
        });
    }
    setIsProcessedPosted({ ...isProcessedPosted, ...dict });
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
      switch (idx) {
        case 0:
          if (value < 0) {
            temp = {
              ...temp,
              [e.target.name]: processed_minute[valueIdx][e.target.name] || '',
            };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
          } else {
            temp = { ...temp, [e.target.name]: value };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
          }
        case 1:
          if ((value !== '' && value >= 0 && value < 1) || value > 10) {
            temp = {
              ...temp,
              [e.target.name]: processed_data[valueIdx][e.target.name] || '',
            };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
          } else {
            temp = { ...temp, [e.target.name]: value };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
          }
          break;
        case 2:
          if ((value !== '' && value >= 0 && value < 1) || value > 10) {
            temp = {
              ...temp,
              [e.target.name]: heated_data[valueIdx][e.target.name] || '',
            };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
          } else {
            temp = { ...temp, [e.target.name]: value };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
          }
          break;
        case 3:
          if (
            (e.target.name === 'DL' ||
              e.target.name === 'CL' ||
              e.target.name === 'RW') &&
            value > 100
          ) {
            temp = {
              ...temp,
              [e.target.name]: lab_data[valueIdx][e.target.name] || '',
            };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
          } else {
            temp = { ...temp, [e.target.name]: value };
            setInputFields[idx].setter((currentField) => ({
              ...currentField,
              [valueIdx]: temp,
            }));
            break;
          }
          break;
        default:
          break;
      }
      console.log('result', temp, valueIdx);
    }
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
              <RawTable data={rawInput} />
            </Tab>
            <Tab
              value="proc"
              eventKey="processedMeat"
              title="처리육"
              style={{ backgroundColor: 'white' }}
            >
              {processed_data.length !== 0 ? (
                <>
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
                  <ProcessedTable
                    edited={edited}
                    modal={modal}
                    setModal={setModal}
                    processed_img_path={processed_img_path}
                    processedMinute={processedMinute}
                    setProcessedMinute={setProcessedMinute}
                    processedInput={processedInput}
                    processed_data={processed_data}
                    processedToggleValue={processedToggleValue}
                    handleInputChange={handleInputChange}
                  />
                </>
              ) : (
                <div style={divStyle.errorContainer}>
                  <div style={divStyle.errorText}>처리육 데이터가 없습니다</div>
                </div>
              )}
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
              <HeatTable
                edited={edited}
                heatInput={heatInput}
                heated_data={heated_data}
                heatedToggleValue={heatedToggleValue}
                handleInputChange={handleInputChange}
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
              <LabTable
                edited={edited}
                labInput={labInput}
                lab_data={lab_data}
                labToggleValue={labToggleValue}
                handleInputChange={handleInputChange}
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
}

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

const style = {
  singleDataWrapper: {
    marginTop: '40px',
    display: 'flex',
    justifyContent: 'space-between',
  },
  editBtnWrapper: {
    padding: '0px',
    margin: '10px 0px 0px',
    paddingRight: '10px',
    width: '100%',
    display: 'flex',
    justifyContent: 'end',
    minWidth: '1140px',
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
    width: '60px',
    borderRight: '0.8px solid #e0e0e0',
    padding: '4px 5px',
  },
  completeBtn: {
    border: `1px solid ${navy}`,
    color: `${navy}`,
    borderRadius: '5px',
    width: '60px',
    height: '35px',
  },
  editBtn: {
    backgroundColor: `${navy}`,
    border: 'none',
    color: 'white',
    borderRadius: '5px',
    width: '60px',
    height: '35px',
  },
};
const divStyle = {
  currDiv: {
    height: 'fit-content',
    width: 'fit-content',
    padding: '10px',
    borderRadius: '5px',
    color: navy,
  },
  notCurrDiv: {
    height: '100%',
    width: 'fit-content',
    borderRadius: '5px',
    padding: '10px',
    color: '#b0bec5',
  },
  loadingBackground: {
    position: 'absolute',
    width: '100vw',
    height: '100vh',
    top: 0,
    left: 0,
    backgroundColor: '#ffffffb7',
    zIndex: 999,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: '25px',
    textAlign: 'center',
  },
  errorContainer: {
    height: '65vh',
    minHeight: '500px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
  },
  errorText: {
    fontSize: '16px',
    textAlign: 'center',
  },
};
