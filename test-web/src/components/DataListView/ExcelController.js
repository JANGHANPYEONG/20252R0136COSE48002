import { useState, useEffect, useRef } from 'react';
import { ExcelRenderer } from 'react-excel-renderer';
import ArrowDownOnSquareIcon from '@heroicons/react/24/solid/ArrowDownOnSquareIcon';
import ArrowUpOnSquareIcon from '@heroicons/react/24/solid/ArrowUpOnSquareIcon';
import { Box, Button, SvgIcon, CircularProgress } from '@mui/material';
import { getDataListJSON, downloadExcel } from './excelExport';
import { apiIP } from '../../config';
import ExcelImportAlertModal from './Children/ExcelImportAlertModal';
import style from './style/excelcontrollerstyle';
import { useUser } from '../../Utils/UserContext';

const ExcelController = ({ startDate, endDate, specieValue }) => {
  // UserContext에서 유저 정보 불러오기
  const user = useUser();
  // 엑셀 업로드 성공 여부
  const [isImportSuccessed, setIsImportSuccessed] = useState(true);
  // 엑셀 업로드 완료
  const [alertDone, setAlertDone] = useState(false);
  // 로딩 상태
  const [isLoading, setIsLoading] = useState(false);

  const fileRef = useRef(null);

  // 파일 선택 함수
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    await handleExcelFile(file);
    setAlertDone(true);
  };

  // 선택한 엑셀 파일을 json으로 변환한 뒤 추가 API로 전송
  const handleExcelFile = async (file) => {
    // 엑셀 시트를 JSON 객체로 변경
    ExcelRenderer(file, (err, resp) => {
      // 변경 중 에러가 난 경우
      if (err) {
        console.log(err);
      }
      // 정상적으로 변경된 경우
      else {
        for (let index = 1; index < resp.rows.length; index++) {
          // 엑셀 파일에서 관리번호를 추출
          const id = resp.rows[index][0];
          // 파일 최종 수정 시간
          const lastModified = file.lastModified;

          // 가열육 수정 정보를 저장할 객체
          const heatedmeat_eval = {};
          // 처리육 수정 정보를 저장할 객체
          const probexpt_data = {};

          // 엑셀 파일에서 가열육 정보를 추출
          for (let i = 1; i < 6; i++) {
            resp.rows[index][i]
              ? (heatedmeat_eval[resp.rows[0][i]] = resp.rows[index][i])
              : (heatedmeat_eval[resp.rows[0][i]] = null);
          }
          // 엑셀 파일에서 처리육 정보를 추출
          for (let i = 6; i < resp.rows[0].length; i++) {
            resp.rows[index][i]
              ? (probexpt_data[resp.rows[0][i]] = resp.rows[index][i])
              : (probexpt_data[resp.rows[0][i]] = null);
          }

          // 수정 시간 계산
          const lastModifiedDate = file.lastModifiedDate
            .toISOString()
            .slice(0, -5);
          // 수정 이후 period 계산
          const butcheryDate = new Date(2023, 1, 1, 0, 0, 0);
          const elapsedMSec = lastModified - butcheryDate.getTime();
          const elapsedHour = elapsedMSec / 1000 / 60 / 60;
          // 로그인한 유저 정보
          const userId = user.userId;

          // 1.1 가열육 관능평가 데이터 JSON으로 변환
          let heatedmeatEvalReq = heatedmeat_eval;
          heatedmeatEvalReq = {
            ...heatedmeatEvalReq,
            ['id']: id,
            ['createdAt']: lastModifiedDate,
            ['userId']: userId,
            ['seqno']: 0,
            ['period']: Math.round(elapsedHour),
          };
          // 1.2 가열육 관능평가 데이터 수정 요청 API
          try {
            const response = fetch(`http://${apiIP}/meat/add/heatedmeat-eval`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(heatedmeatEvalReq),
            });
            // 업로드에 성공한 경우
            response.then((res) => {
              if (res.status === 404) {
                setIsImportSuccessed(false);
              }
            });
          } catch (err) {
            console.error(err);
            // 업로드에 실패한 경우
            setIsImportSuccessed(false);
          }

          // 2.1 실험실 데이터 JSON으로 변환
          let probexptReq = probexpt_data;
          probexptReq = {
            ...probexptReq,
            ['id']: id,
            ['updatedAt']: lastModifiedDate,
            ['userId']: userId,
            ['seqno']: 0,
            ['period']: Math.round(elapsedHour),
          };

          // 2.2 실험실 데이터 수정 요청 API
          try {
            const response = fetch(`http://${apiIP}/meat/add/probexpt-data`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(probexptReq),
            });
            // 업로드에 성공한 경우
            response.then((res) => {
              if (res.status === 404) {
                setIsImportSuccessed(false);
              }
            });
          } catch (err) {
            console.error(err);
            // 업로드에 실패한 경우
            setIsImportSuccessed(false);
          }
        }
      }
    });
  };

  // excel export 시 다운로드 할 데이터 목록
  const [excelData, setExcelData] = useState();

  // excel export 버튼 클릭 시
  const handleExcelExport = () => {
    // 'excelData'를 인자로 다운로드 함수 호출
    downloadExcel(excelData);
  };

  // excel export할 목록 데이터 fetch
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const data = await getDataListJSON({ startDate, endDate, specieValue });
      setExcelData(data);
      setIsLoading(false);
    };

    fetchData();
  }, [startDate, endDate, specieValue]);

  return (
    <Box>
      {alertDone && (
        <ExcelImportAlertModal
          setAlertDone={setAlertDone}
          isImportSuccessed={isImportSuccessed}
          setIsImportSuccessed={setIsImportSuccessed}
        />
      )}
      <input
        className="form-control"
        accept=".csv,.xlsx,.xls"
        type="file"
        id="formFile"
        ref={fileRef}
        onChange={(e) => {
          handleFileChange(e);
        }}
        style={{ display: 'none' }}
      />

      {/* <Button
        style={style.importBtnWrapper}
        onClick={() => {
          fileRef.current.click();
        }}
      >
        <div style={{ display: 'flex' }}>
          <SvgIcon fontSize="small">
            <ArrowUpOnSquareIcon />
          </SvgIcon>
          <span>Import</span>
        </div>
      </Button> */}

      {isLoading ? (
        <CircularProgress />
      ) : (
        <Button
          style={style.exportBtnWrapper}
          onClick={handleExcelExport}
          disabled={!excelData}
        >
          <div style={{ display: 'flex' }}>
            <SvgIcon fontSize="small">
              <ArrowDownOnSquareIcon />
            </SvgIcon>
            <span>Export</span>
          </div>
        </Button>
      )}
    </Box>
  );
};

export default ExcelController;
