import { useState, useEffect } from 'react';
import Card from 'react-bootstrap/Card';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Spinner from 'react-bootstrap/Spinner';
import QRInfoCard from './cardComps/QRInfoCard';
//mui
import './imgRot.css';
import { TextField, Autocomplete } from '@mui/material';
// import tables
import RawTable from './tablesComps/rawTable';
import PredictedRawTable from './tablesComps/predictedRawTable';
import ProcessedTableStatic from './tablesComps/processedTableStatic';
import PredictedProcessedTablePA from './tablesComps/predictedProcessedTablePA';

import { computePeriod } from './computePeriod';
import { apiIP } from '../../config';

function DataPAView({ dataProps }) {
  //데이터 받아오기
  const {
    meatId, // 이력번호
    userId, // 로그인한 사용자 id
    createdAt, // 생성 시간
    qrImagePath, // QR이미지 경로
    raw_img_path, // 원육 이미지 경로
    raw_data, // 원육 데이터
    processed_data, // 처리육 데이터
    api_data, // 축산물 이력 API 데이터
    processed_data_seq, // 처리(딥에이징) 회차
    processed_minute, // 처리 시간 (분)
    processed_img_path, // 처리육 이미지 경로
  } = dataProps;

  // 처리육 및 실험 회차 토글
  useEffect(() => {
    options = processed_data_seq;
  }, []);

  // 처리육 토글
  const [processed_toggle, setProcessedToggle] = useState('1회');
  const [processedToggleValue, setProcessedToggleValue] = useState('1회');

  //이미지 파일
  const [previewImage, setPreviewImage] = useState(raw_img_path);
  const [dataXAIImg, setDataXAIImg] = useState(null);
  const [gradeXAIImg, setGradeXAIImg] = useState(null);

  // fetch 한 예측 데이터 저장
  const [dataPA, setDataPA] = useState(null);
  // 예측 데이터 fetch
  const getPredictedData = async (seqno) => {
    try {
      const response = await fetch(
        `http://${apiIP}/meat/get/predict-data?id=${id}&seqno=${seqno}`
      );
      if (!response.ok) {
        throw new Error('Network response was not ok', id, '-', seqno);
      }
      const json = await response.json();
      setDataPA(json);
      setDataXAIImg(json.xai_imagePath);
      setGradeXAIImg(json.xai_gradeNum_imagePath);
      return json;
    } catch (error) {
      // 데이터를 불러오는 데 실패한 경우 모든 data를 null로 설정
      console.error('Error fetching data seqno-', seqno, ':', error);
      setDataPA(null);
      setDataXAIImg(null);
      setGradeXAIImg(null);
    }
  };

  //예측 post 중 로딩 표시
  const [isPredictedDone, SetIsPredictedDone] = useState(true);

  //데이터 예측 버튼 클릭 시
  const handlePredictClick = async () => {
    //로그인한 유저 정보
    const userId = JSON.parse(localStorage.getItem('UserInfo'))['userId'];
    // period 계산
    const elapsedHour = computePeriod(api_data['butcheryYmd']);
    const len = processed_data_seq.length;

    // 로딩 화면 표시 시작
    SetIsPredictedDone(false);
    //모든 육류 데이터 (원육, n회차 이미지)에 대해 예측
    for (let i = 0; i < len; i++) {
      let req = {
        ['id']: id,
        ['seqno']: i,
        ['userId']: userId,
        ['period']: Math.round(elapsedHour),
      };
      try {
        await fetch(`http://${apiIP}/meat/get/predict-data`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(req),
        });
        // 예측 정보 로드
        await getPredictedData(i);
      } catch (err) {
        console.error(err);
      }
    }
    // 로딩 화면 표시 종료
    SetIsPredictedDone(true);
  };

  //탭 변환에 맞는 데이터 로드
  const handleSelect = async (key) => {
    // 예측 데이터 로드
    await getPredictedData(key);
    // 원본 이미지 바꾸기
    key === '0'
      ? setPreviewImage(raw_img_path)
      : setPreviewImage(
          processed_img_path[parseInt(processedToggleValue) - 1]
            ? processed_img_path[parseInt(processedToggleValue) - 1]
            : null
        );
  };

  // 처리육 탭에서 회차가 바뀜에 따라 다른 예측 결과 load
  useEffect(() => {
    getPredictedData(parseInt(processedToggleValue));
  }, [processedToggleValue]);

  // 초기에 원육 예측 데이터 로드
  useEffect(() => {
    getPredictedData(0);
  }, []);

  return (
    <div style={{ width: '100%' }}>
      {!isPredictedDone && (
        <div style={divStyle.loadingBackground}>
          <Spinner />
          <span style={divStyle.loadingText}>
            맛 데이터 및 등급을 예측 중 입니다..
          </span>
        </div>
      )}
      <div style={style.editBtnWrapper}>
        <button
          type="button"
          class="btn btn-outline-success"
          onClick={handlePredictClick}
        >
          예측
        </button>
      </div>
      <div style={style.singleDataWrapper}>
        {/* 1. 관리번호 육류에 대한 사진*/}
        <div>
          {/* 1.1. 원본이미지 */}
          <Card style={style.imgContainer}>
            <Card.Body>
              <Card.Text>
                <div style={style.imgTextWrapper}>원본이미지</div>
                <div style={style.imgWrapper}>
                  {previewImage ? (
                    <img
                      src={previewImage + '?n=' + Math.random()}
                      style={style.imgWrapperContextImg}
                    />
                  ) : (
                    <div style={style.imgWrapperContextText}>
                      데이터 이미지가 존재하지 않습니다.
                    </div>
                  )}
                </div>
              </Card.Text>
            </Card.Body>
          </Card>
          {/** 1.2. XAI 이미지 */}
          <Card style={style.xaiImgContainer}>
            <Card.Body>
              <Card.Text>
                <div style={style.imgTextWrapper}>
                  XAI이미지 [데이터/등급예측]
                </div>
                <div style={style.xaiImageWrapper}>
                  {dataXAIImg ? (
                    <div className="imgContainer">
                      <img
                        src={dataXAIImg + '?n=' + Math.random()}
                        style={style.imgWrapperContextImg}
                      />
                    </div>
                  ) : (
                    <div style={style.imgWrapperContextText}>
                      데이터 XAI 이미지가 존재하지 않습니다.
                    </div>
                  )}
                  <div style={{ width: '30px' }}></div>
                  {gradeXAIImg ? (
                    <div className="imgContainer">
                      <img
                        src={gradeXAIImg + '?n=' + Math.random()}
                        style={style.imgWrapperContextImg}
                      />
                    </div>
                  ) : (
                    <div style={style.imgWrapperContextText}>
                      등급 XAI 이미지가 존재하지 않습니다.
                    </div>
                  )}
                </div>
              </Card.Text>
            </Card.Body>
          </Card>
        </div>
        {/* 2. QR코드와 데이터에 대한 기본 정보*/}
        <QRInfoCard
          qrImagePath={qrImagePath}
          id={id}
          userId={userId}
          createdAt={createdAt}
          page="predict"
          divStyle={style.qrWrapper}
        />
        {/* 3. 세부 데이터 정보*/}
        <Card
          style={{
            width: '24vw',
            margin: '0px 10px',
            boxShadow: 24,
            minWidth: '360px',
          }}
        >
          <Tabs
            defaultActiveKey="0"
            id="uncontrolled-tab-example"
            className="mb-3"
            style={{ backgroundColor: 'white', width: '100%' }}
            onSelect={handleSelect}
          >
            <Tab eventKey="0" title="원육" style={{ backgroundColor: 'white' }}>
              <RawTable data={raw_data} />
              <PredictedRawTable raw_data={raw_data} dataPA={dataPA} />
            </Tab>
            <Tab
              eventKey="1"
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
                  setProcessedToggleValue(newInputValue);
                  /*이미지 변경 */
                  setPreviewImage(
                    processed_img_path[parseInt(newInputValue) - 1]
                      ? processed_img_path[parseInt(newInputValue) - 1]
                      : null
                  );
                }}
                options={options.slice(1)}
                size="small"
                sx={{ width: 300, marginBottom: '10px' }}
                renderInput={(params) => <TextField {...params} />}
              />
              <ProcessedTableStatic
                processedMinute={processed_minute}
                processedToggleValue={processedToggleValue}
                processed_data={processed_data}
              />
              <PredictedProcessedTablePA
                seqno={parseInt(processedToggleValue)}
                processed_data={processed_data}
                dataPA={dataPA}
              />
            </Tab>
          </Tabs>
        </Card>
      </div>
    </div>
  );
}

export default DataPAView;

// 토글 버튼
let options = ['원육'];

const style = {
  singleDataWrapper: {
    height: 'fit-content',
    marginTop: '10px',
    display: 'flex',
    justifyContent: 'space-between',
    width: '100%',
  },
  editBtnWrapper: {
    padding: '0px',
    margin: '0px',
    paddingRight: '10px',
    width: '100%',
    display: 'flex',
    justifyContent: 'end',
    borderBottomLeftRadius: '10px',
    borderBottomRightRadius: '10px',
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
    width: '',
    borderRight: '0.8px solid #e0e0e0',
    padding: '4px 5px',
    display: 'flex',
  },
  imgContainer: {
    width: '23vw',
    margin: '0px 10px',
    marginBottom: '20px',
    boxShadow: 24,
    minWidth: '360px',
  },
  imgTextWrapper: {
    color: '#002984',
    fontSize: '18px',
    fontWeight: '800',
  },
  imgWrapper: {
    width: '100%',
    padding: '10px 0px',
    borderRadius: '10px',
  },
  imgWrapperContextImg: {
    height: '190px',
    width: '100%',
    objectFit: 'contain',
  },
  imgWrapperContextText: {
    height: '190px',
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  xaiImgContainer: {
    width: '23vw',
    margin: '0px 10px',
    boxShadow: 24,
    minWidth: '360px',
  },
  xaiImageWrapper: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    padding: '10px 0px',
  },
  qrWrapper: {
    width: '23vw',
    margin: '0px 10px',
    boxShadow: 24,
    minWidth: '360px',
  },
};
const divStyle = {
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
};
