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
import ApiTable from './TablesComps/ApiTable';
// import timezone
import { TIME_ZONE } from '../../config';
import Spinner from 'react-bootstrap/Spinner';
// import update APIs

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
import { rawField, apiField } from './constants/infofield';

const navy = '#0F3659';

const DataConfirmView = ({ dataProps }) => {
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
    api_data, // 축산물 이력 API 데이터
    processed_img_path,
  } = dataProps;
  //탭 정보
  const tabFields = [rawField, apiField];
  // 탭별 데이터 -> datas는 불변 , input text를 바꾸고 서버에 전송
  const datas = [raw_data, api_data];

  // "원육", "축산물 이력",별 수정 및 추가 input text
  const [rawInput, setRawInput] = useState({});
  const [apiInput, setApiInput] = useState(api_data);
  // setInputFields를 통해 인덱스 값으로 수정할 Field를 접근
  const setInputFields = [
    { value: rawInput, setter: setRawInput },
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

    //1. 원육 데이터 수정 API
    addSensoryRawData(rawInput, 0, meatId)
      .then((response) => {
        console.log('원육 수정 POST요청 성공:', response);
      })
      .catch((error) => {
        // 오류 발생 시의 처리
        console.error('원육 수정 POST 요청 오류:', error);
      });
  };

  const handleRawInputChange = (e, field) => {
    const { name, value } = e.target;
    setRawInput((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

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
    </div>
  );
};

export default DataConfirmView;

// 토글 버튼
let options = ['원육'];
