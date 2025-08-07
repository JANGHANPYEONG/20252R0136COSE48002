import React, { useState, useRef, useEffect } from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import * as XLSX from 'xlsx';
import JSZip from 'jszip';
import style from './style/dashboardstyle';
import DataListWithURL from '../components/DataListWithURL';
import uploadDataToServer from '../API/add/uploadDataToServer'; // 새로운 API import

const navy = '#0F3659';

const DataRegister = () => {
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [csvLoading, setCsvLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState(''); // 성공 메시지 상태
  const [uploadedZipFile, setUploadedZipFile] = useState(null); // ZIP 파일 상태 추가

  const fileInputRef = useRef(null);

  // 파일을 Base64로 변환하는 유틸리티 함수
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // 컴포넌트 마운트 시 localStorage에서 CSV 데이터만 복원
  useEffect(() => {
    const savedData = localStorage.getItem('dataRegister_data');
    const savedColumns = localStorage.getItem('dataRegister_columns');
    
    if (savedData && savedColumns) {
      try {
        const parsedData = JSON.parse(savedData);
        const parsedColumns = JSON.parse(savedColumns);
        
        // 이미지 관련 컬럼 제거 및 상태 초기화 (이미지_URL 제외)
        const cleanColumns = parsedColumns.filter(col => 
          !['이미지 파일명', '이미지 개수'].includes(col)
        );
        const cleanData = parsedData.map(row => {
          const { '이미지 파일명': 이미지파일명, '이미지 개수': 이미지개수, ...cleanRow } = row;
          // 매핑 상태를 매핑안됨으로 초기화
          cleanRow['매핑 상태'] = '매핑안됨';
          return cleanRow;
        });
        
        setData(cleanData);
        setColumns(cleanColumns);
        console.log('CSV 데이터만 복원:', cleanData.length, '개 항목');
      } catch (error) {
        console.error('데이터 복원 오류:', error);
        // 오류 발생 시 localStorage 정리
        localStorage.removeItem('dataRegister_data');
        localStorage.removeItem('dataRegister_columns');
      }
    }
  }, []);

  // CSV 데이터 변경 시에만 localStorage에 저장 (이미지 데이터 제외)
  useEffect(() => {
    if (data.length > 0 && columns.length > 0) {
      try {
        // 이미지 관련 데이터를 제외한 CSV 데이터만 저장 (이미지_URL 제외)
        const csvColumns = columns.filter(col => 
          !['이미지 파일명', '이미지 개수'].includes(col)
        );
        const csvData = data.map(row => {
          const { '이미지 파일명': 이미지파일명, '이미지 개수': 이미지개수, ...csvRow } = row;
          // 매핑 상태는 매핑안됨으로 저장
          csvRow['매핑 상태'] = '매핑안됨';
          return csvRow;
        });
        
        localStorage.setItem('dataRegister_data', JSON.stringify(csvData));
        localStorage.setItem('dataRegister_columns', JSON.stringify(csvColumns));
      } catch (error) {
        console.error('localStorage 저장 오류:', error);
      }
    }
  }, [data, columns]);

  const handleLoadClick = () => fileInputRef.current?.click();
  
  const handleImageClick = () => {
    // ZIP 파일만 허용하는 이미지 업로드 input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.zip'; // ZIP 파일만 허용
    input.addEventListener('change', handleZipImageUpload);
    input.click();
  };

  const handleRegister = async () => {
    try {
      // 1. 데이터 존재 여부 확인
      if (!data || data.length === 0) {
        alert('업로드할 데이터가 없습니다. 먼저 CSV 파일을 업로드해주세요.');
        return;
      }

      // 2. ZIP 파일 존재 여부 확인
      if (!uploadedZipFile) {
        alert('ZIP 파일이 업로드되지 않았습니다. 먼저 ZIP 파일을 업로드해주세요.');
        return;
      }

      // 3. 매핑 상태 확인
      const unmappedData = data.filter(row => 
        row['매핑 상태'] === '매핑안됨' || 
        !row['매핑 상태'] || 
        row['매핑 상태'] === ''
      );

      if (unmappedData.length > 0) {
        alert(`매핑되지 않은 데이터가 ${unmappedData.length}개 있습니다.\n모든 데이터를 매핑한 후 다시 시도해주세요.`);
        return;
      }

      setLoading(true);
      
      // 4. 서버에 데이터 업로드
      const result = await uploadDataToServer(data, columns, uploadedZipFile);
      
      if (result.success) {
        alert('데이터 등록이 성공적으로 완료되었습니다!');
        showSuccessMessage('데이터 등록 완료!');
        
        // 등록 성공 시 모든 데이터 초기화
        clearData();
        setUploadedZipFile(null);
      } else {
        alert(`데이터 등록에 실패했습니다.\n오류: ${result.message}`);
      }
      
    } catch (err) {
      console.error('데이터 등록 오류:', err);
      alert(`데이터 등록 중 오류가 발생했습니다.\n${err.message || '알 수 없는 오류가 발생했습니다.'}`);
    } finally {
      setLoading(false);
    }
  };

  // 데이터 초기화 함수
  const clearData = () => {
    setColumns([]);
    setData([]);
    setUploadedZipFile(null); // ZIP 파일 상태도 초기화
    localStorage.removeItem('dataRegister_data');
    localStorage.removeItem('dataRegister_columns');
    console.log('모든 데이터가 초기화되었습니다.');
  };

  // 성공 메시지 표시 함수
  const showSuccessMessage = (message) => {
    setSuccessMessage(message);
    setTimeout(() => {
      setSuccessMessage('');
    }, 3000); // 3초 후 사라짐
  };

  // 데이터 삭제 함수 (확인 후 삭제)
  const handleDeleteData = () => {
    if (window.confirm('저장된 모든 데이터를 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')) {
      clearData();
      showSuccessMessage('모든 데이터가 삭제되었습니다.');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // CSV 파일만 허용
    if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.xlsx')) {
      alert('CSV 또는 Excel 파일만 업로드 가능합니다.');
      return;
    }
    
    setCsvLoading(true);
    const reader = new FileReader();
    
    reader.onload = (evt) => {
      try {
        let rowsArray = [];
        
        if (file.name.toLowerCase().endsWith('.csv')) {
          // CSV 파일 처리
          const csvText = evt.target.result;
          const lines = csvText.split('\n');
          rowsArray = lines.map(line => {
            // CSV 파싱 (간단한 버전, 콤마로 구분)
            return line.split(',').map(cell => cell.trim().replace(/"/g, ''));
          }).filter(row => row.some(cell => cell !== ''));
        } else {
          // Excel 파일 처리
          const wb = XLSX.read(evt.target.result, { type: 'array' });
          const sheet = wb.Sheets[wb.SheetNames[0]];
          rowsArray = XLSX.utils.sheet_to_json(sheet, {
            header: 1,
            defval: '',
          });
        }
        
        if (!rowsArray.length) {
          setColumns([]);
          setData([]);
          setCsvLoading(false);
          return;
        }
        
        // 헤더 처리
        const origHeader = rowsArray[0].map(String);
        const validIdx = origHeader
          .map((h, i) => ({ h: h.trim(), i }))
          .filter(({ h }) => h !== '')
          .map(({ i }) => i);
        const filteredHeaders = validIdx.map((i) => origHeader[i]);

        // 데이터 행 처리
        const dataRows = rowsArray
          .slice(1)
          .filter((r) => r.some((c) => c !== ''));
        const mapped = dataRows.map((rowArr) => {
          const obj = {};
          // 상태 컬럼을 먼저 추가 (초기값: 매핑안됨)
          obj['매핑 상태'] = '매핑안됨';
          validIdx.forEach((i, idx) => {
            obj[filteredHeaders[idx]] = rowArr[i];
          });
          return obj;
        });

        // 상태 컬럼을 맨 앞에 추가
        const columnsWithStatus = ['매핑 상태', ...filteredHeaders];
        setColumns(columnsWithStatus);
        setData(mapped);
        console.log('CSV 데이터 로드 완료:', mapped.length, '개 항목');
      } catch (error) {
        console.error('파일 처리 오류:', error);
        alert('파일 처리 중 오류가 발생했습니다.');
      } finally {
        setCsvLoading(false);
      }
    };
    
    if (file.name.toLowerCase().endsWith('.csv')) {
      reader.readAsText(file);
    } else {
      reader.readAsArrayBuffer(file);
    }
    e.target.value = null;
  };

  // ZIP 파일 전용 이미지 업로드 처리
  const handleZipImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // ZIP 파일인지 확인
    if (!file.name.toLowerCase().endsWith('.zip')) {
      alert('ZIP 파일만 업로드 가능합니다.');
      return;
    }
    
    setImageLoading(true);
    
    try {
      console.log('ZIP 파일 처리:', file.name);
      setUploadedZipFile(file); // ZIP 파일을 상태에 저장
      await handleZipFile(file);
    } catch (error) {
      console.error('ZIP 파일 처리 오류:', error);
      alert('ZIP 파일 처리 중 오류가 발생했습니다.');
      setUploadedZipFile(null); // 오류 시 ZIP 파일 상태 초기화
    } finally {
      setImageLoading(false);
    }
  };

  // ZIP 파일 처리
  const handleZipFile = async (zipFile) => {
    try {
      const zip = new JSZip();
      const zipData = await zip.loadAsync(zipFile);
      const imageMap = {};
      
      // ZIP 파일 내의 모든 파일을 순회
      for (const [fileName, fileObj] of Object.entries(zipData.files)) {
        if (fileObj.dir) continue; // 폴더는 건너뛰기
        
        // 이미지 파일 확인
        const isImage = /\.(jpg|jpeg|png|gif|bmp)$/i.test(fileName);
        if (!isImage) continue;
        
        // 파일 경로에서 ID 추출
        const pathParts = fileName.split('/');
        let id = null;
        let imageNumber = null;
        
        if (pathParts.length > 1) {
          // 폴더 구조: ID/ID_P숫자.확장자 (예: O0260_R01_N112/O0260_R01_N112_P10.png)
          id = pathParts[pathParts.length - 2]; // 폴더명이 ID
          const imageFileName = pathParts[pathParts.length - 1];
          
          // ID_P숫자.확장자 패턴 매칭
          const match = imageFileName.match(/^(.+)_P(\d+)\./);
          if (match && match[1] === id) {
            imageNumber = match[2]; // P 뒤의 숫자
          }
        } else {
          // 직접 파일: ID_P숫자.확장자 패턴
          const match = fileName.match(/^(.+)_P(\d+)\./);
          if (match) {
            id = match[1];
            imageNumber = match[2];
          }
        }
        
        if (id && imageNumber) {
          if (!imageMap[id]) {
            imageMap[id] = {};
          }
          
          // 파일 데이터를 Blob URL로 변환
          const blob = await fileObj.async('blob');
          const objectUrl = URL.createObjectURL(blob);
          
          imageMap[id][imageNumber] = {
            fileName: fileName.split('/').pop(),
            url: objectUrl, // 임시 URL 사용
            number: imageNumber
          };
        }
      }
      
      // 기존 데이터와 매칭
      await matchImagesWithData(imageMap);
      
    } catch (error) {
      console.error('ZIP 파일 처리 오류:', error);
      throw error;
    }
  };

  // 이미지와 데이터 매칭
  const matchImagesWithData = async (imageMap) => {
    if (!columns.length) {
      alert('먼저 CSV 파일을 업로드해주세요.');
      return;
    }
    
    // ID 컬럼 찾기
    const idColumn = columns.find(col => 
      col.toLowerCase().includes('id') || 
      col.toLowerCase().includes('ID') ||
      col === 'ID' ||
      col === 'id'
    );
    
    if (!idColumn) {
      alert('CSV 파일에서 ID 컬럼을 찾을 수 없습니다.');
      return;
    }
    
    // 상태 컬럼과 이미지 관련 컬럼 추가 (이미지_URL 제외)
    const statusColumn = '매핑 상태';
    const imageColumns = ['이미지 파일명', '이미지 개수']; // 이미지_URL 제거
    
    // 기존 컬럼에서 매핑_상태가 이미 있는지 확인
    let newColumns = [...columns];
    
    // 매핑_상태가 없으면 맨 앞에 추가
    if (!newColumns.includes(statusColumn)) {
      newColumns = [statusColumn, ...newColumns];
    }
    
    // 이미지 관련 컬럼들 추가 (중복 확인)
    imageColumns.forEach(col => {
      if (!newColumns.includes(col)) {
        newColumns.push(col);
      }
    });
    
    // 기존 데이터 업데이트 및 새로운 데이터 추가
    const updatedData = [...data];
    const existingIds = new Set(data.map(row => String(row[idColumn])));
    
    // 기존 데이터 업데이트
    updatedData.forEach(row => {
      const rowId = String(row[idColumn]);
      if (imageMap[rowId]) {
        const images = Object.values(imageMap[rowId]);
        row[statusColumn] = '매핑됨';
        row['이미지 파일명'] = images.map(img => img.fileName).join(', ');
        row['이미지 개수'] = images.length;
      } else {
        row[statusColumn] = '매핑안됨';
        row['이미지 파일명'] = '';
        row['이미지 개수'] = 0;
      }
    });
    
    // 새로운 ID 데이터 추가 (CSV에 없지만 이미지에는 있는 경우)
    Object.keys(imageMap).forEach(imageId => {
      if (!existingIds.has(imageId)) {
        const images = Object.values(imageMap[imageId]);
        const newRow = {};
        
        // 상태 컬럼 먼저 설정
        newRow[statusColumn] = '매핑됨';
        
        // 기존 컬럼들을 빈 값으로 초기화
        columns.forEach(col => {
          newRow[col] = col === idColumn ? imageId : '';
        });
        
        // 이미지 정보 추가 (URL 제외)
        newRow['이미지 파일명'] = images.map(img => img.fileName).join(', ');
        newRow['이미지 개수'] = images.length;
        
        updatedData.push(newRow);
      }
    });
    
    setColumns(newColumns);
    setData(updatedData);
    
    console.log('이미지 매칭 완료:', Object.keys(imageMap).length, '개 ID의 이미지 처리됨');
  };

  return (
    <div
      style={{
        overflow: 'auto',
        width: '100%',
        marginTop: '100px',
        height: '100%',
        paddingLeft: '30px',
        paddingRight: '20px',
        position: 'relative', // 성공 메시지 위치를 위한 상대 위치
      }}
    >
      {/* 성공 메시지 알림 */}
      {successMessage && (
        <Box
          sx={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            backgroundColor: '#28a745',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 9999,
            fontSize: '14px',
            fontWeight: '500',
            animation: 'slideIn 0.3s ease-out',
            '@keyframes slideIn': {
              from: { transform: 'translateX(100%)', opacity: 0 },
              to: { transform: 'translateX(0)', opacity: 1 }
            }
          }}
        >
          ✅ {successMessage}
        </Box>
      )}
      
      <Box
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          minWidth: '634px',
        }}
      >
        <span style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}>
          데이터 등록
        </span>
      </Box>

      {/* 숨겨진 입력들 */}
      <input
        type="file"
        accept=".csv,.xlsx"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      {/* 버튼 영역 */}
      <Box
        sx={{
          ...style.fixedTab,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          mb: 4,
        }}
      >
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleLoadClick}
            disabled={csvLoading || imageLoading}
            sx={{
              backgroundColor: navy,
              '&:hover': { backgroundColor: '#0a2a4a' },
            }}
          >
            {csvLoading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              'CSV 불러오기'
            )}
          </Button>
          <Button
            variant="contained"
            onClick={handleImageClick}
            disabled={csvLoading || imageLoading}
            sx={{
              backgroundColor: navy,
              '&:hover': { backgroundColor: '#0a2a4a' },
            }}
          >
            {imageLoading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              '사진 불러오기(ZIP)'
            )}
          </Button>
          {data.length > 0 && (
            <Button
              variant="outlined"
              onClick={handleDeleteData}
              sx={{
                color: '#dc3545',
                borderColor: '#dc3545',
                '&:hover': { 
                  backgroundColor: '#dc3545', 
                  color: 'white',
                  borderColor: '#dc3545'
                },
              }}
            >
              전체 삭제
            </Button>
          )}
        </Box>
        
        {/* 우측 버튼 그룹 */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            onClick={handleRegister}
            disabled={
              loading || 
              csvLoading || 
              imageLoading || 
              data.length === 0 || 
              !uploadedZipFile ||
              data.some(row => row['매핑 상태'] === '매핑안됨' || !row['매핑 상태'])
            }
            sx={{
              backgroundColor: data.length > 0 && uploadedZipFile && 
                              !data.some(row => row['매핑 상태'] === '매핑안됨' || !row['매핑 상태']) 
                              ? '#28a745' : '#ccc',
              '&:hover': { 
                backgroundColor: data.length > 0 && uploadedZipFile && 
                               !data.some(row => row['매핑 상태'] === '매핑안됨' || !row['매핑 상태']) 
                               ? '#218838' : '#bbb' 
              },
              '&:disabled': { backgroundColor: '#ccc' },
            }}
          >
            {loading ? (
              <>
                <CircularProgress size={20} color="inherit" sx={{ marginRight: '8px' }} />
                업로드 중...
              </>
            ) : (
              '데이터 등록'
            )}
          </Button>
        </Box>
      </Box>

      <DataListWithURL title="미리보기" columns={columns} data={data} />
    </div>
  );
};

export default DataRegister;
