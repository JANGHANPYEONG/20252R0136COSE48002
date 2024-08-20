import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
// react-bootstrap
import Card from 'react-bootstrap/Card';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Button from 'react-bootstrap/Button';
// userContext
import { useUser } from '../../Utils/UserContext';
// modal component
import InputTransitionsModal from './InputTransitionsModal';
// mui
import { TextField, Autocomplete } from '@mui/material';
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
import RestrictedModal from './RestrictedModal';
// import card
import QRInfoCard from './CardComps/QRInfoCard';
import MeatImgsCard from './CardComps/MeatImgsCard';
import { computePeriod } from './computeTime';
import isPost from '../../API/isPost';
import { Modal } from 'react-bootstrap';
import AgingInfoRegister from './AgingInfoRegister';
import AgingInfoDeleter from './AgingInfoDelete';
import style from './style/dataviewstyle';
import { divStyle } from './style/dataviewstyle';
import { rawField, deepAgingField, heatedField, labField, apiField } from './constants/infofield';

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
    processed_date,
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
  const [infoRegisterShow, setInfoRegisterShow] = useState(false);
  const [infoDeleteShow, setInfoDeleteShow] = useState(false);

  const [isProcessedPosted, setIsProcessedPosted] = useState({});
  const [isLabPosted, setIsLabPosted] = useState({});
  const [isHeatedPosted, setIsHeatedPosted] = useState({});

  const handleInfoRegisterShow = () => setInfoRegisterShow(true);
  const handleInfoRegisterClose = () => setInfoRegisterShow(false);
  const handleInfoDeleteShow = () => setInfoDeleteShow(true);
  const handleInfoDeleteClose = () => setInfoDeleteShow(false);
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
    const currentUserId = user.userId;

    // 1. 가열육 관능검사 데이터 생성/수정 API POST/PATCH
    let dict = {};
    for (let i = 0; i < len; i++) {
      const isMethodPost = await isPost(
        [
          heated_data[i]?.flavor,
          heated_data[i]?.juiciness,
          heated_data[i]?.palatability,
          heated_data[i]?.umami,
          heated_data[i]?.tenderness0,
          heated_data[i]?.tenderness3,
          heated_data[i]?.tenderness7,
          heated_data[i]?.tenderness14,
          heated_data[i]?.tenderness21,
        ],
        [
          heatInput[i]?.flavor,
          heatInput[i]?.juiciness,
          heatInput[i]?.palatability,
          heatInput[i]?.umami,
          heatInput[i]?.tenderness0,
          heatInput[i]?.tenderness3,
          heatInput[i]?.tenderness7,
          heatInput[i]?.tenderness14,
          heatInput[i]?.tenderness21,
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
    <>
      <Modal
        show={infoRegisterShow}
        onHide={handleInfoRegisterClose}
        backdrop="true"
        keyboard={false}
        centered
      >
        <Modal.Body>
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
          <AgingInfoRegister
            handleClose={handleInfoRegisterClose}
            processed_data_seq={processed_data_seq}
            meatId={meatId}
          />
        </Modal.Body>
      </Modal>
      <Modal
        show={infoDeleteShow}
        onHide={handleInfoDeleteClose}
        backdrop="true"
        keyboard={false}
        centered
      >
        <Modal.Body>
          <Modal.Title
            style={{
              color: '#151D48',
              fontFamily: 'Poppins',
              fontSize: `24px`,
              fontWeight: 600,
            }}
          >
            딥에이징 회차 삭제
          </Modal.Title>
          <AgingInfoDeleter
            handleClose={handleInfoDeleteClose}
            meatId={meatId}
            processed_data_seq={processed_data_seq}
          />
        </Modal.Body>
      </Modal>
      <div style={{ width: '100%', position: 'relative' }}>
        <Button
          className="mb-3"
          onClick={handleInfoRegisterShow}
          style={{
            position: 'absolute',
            top: 0,
            right: 160,
            display: 'inline-flex',
            paddingX: `${(12 / 1920) * 100}vw`,
            paddingY: `${(16 / 1080) * 100}vh`,
            alignItems: 'center',
            gap: `${(8 / 1920) * 100}vw`,
            borderRadius: `${(10 / 1920) * 100}vw`,
            background: '#32CD32',
            borderColor: '#32CD32',
          }}
        >
          딥에이징 회차 추가
        </Button>
      </div>
      <div style={{ width: '100%', position: 'relative' }}>
        <Button
          className="mb-3"
          onClick={handleInfoDeleteShow}
          style={{
            position: 'absolute',
            top: 0,
            right: 10,
            display: 'inline-flex',
            paddingX: `${(12 / 1920) * 100}vw`,
            paddingY: `${(16 / 1080) * 100}vh`,
            alignItems: 'center',
            gap: `${(8 / 1920) * 100}vw`,
            borderRadius: `${(10 / 1920) * 100}vw`,
            background: 'red',
            borderColor: 'red',
          }}
        >
          딥에이징 회차 삭제
        </Button>
      </div>
      <div style={{ width: '100%', marginTop: '40px' }}>
        {!isUploadingDone && (
          <div style={divStyle.loadingBackground}>
            <Spinner />
            <span style={divStyle.loadingText}>
              이미지를 업로드 중 입니다..
            </span>
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
                        setProcessedToggleValue(
                          newInputValue
                        ); /*이미지 바꾸기 */
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
                      processed_date={processed_date}
                      processed_data_seq={processed_data_seq}
                    />
                  </>
                ) : (
                  <div style={divStyle.errorContainer}>
                    <div style={divStyle.errorText}>
                      처리육 데이터가 없습니다
                    </div>
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
                  processed_data_seq={processed_data_seq}
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
                  processed_data_seq={processed_data_seq}
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
            <button
              type="button"
              style={style.editBtn}
              onClick={onClickEditBtn}
            >
              수정
            </button>
          )}
        </div>
      </div>
    </>
  );
};

export default DataView;

// 토글 버튼
let options = ['원육'];