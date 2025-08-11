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
          // CSV 파일 처리 - 개선된 파싱
          const csvText = evt.target.result;
          const lines = csvText.split('\n');
          rowsArray = lines.map(line => {
            // 개선된 CSV 파싱 - RFC 4180 호환
            const result = [];
            let current = '';
            let inQuotes = false;
            
            for (let i = 0; i < line.length; i++) {
              const char = line[i];
              const nextChar = line[i + 1];
              
              if (char === '"') {
                if (inQuotes && nextChar === '"') {
                  // 연속된 따옴표는 이스케이프된 따옴표
                  current += '"';
                  i++; // 다음 문자 건너뛰기
                } else {
                  // 따옴표 상태 토글
                  inQuotes = !inQuotes;
                }
              } else if (char === ',' && !inQuotes) {
                // 따옴표 밖의 콤마는 구분자
                result.push(current.trim());
                current = '';
              } else {
                current += char;
              }
            }
            
            // 마지막 셀 추가
            result.push(current.trim());
            
            return result;
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
        
        // 날짜 형식 변환 함수
        const formatDateValue = (value, columnName) => {
          if (!value) return value;
          
          // 날짜 관련 컬럼인지 확인
          const isDateColumn = columnName && (
            columnName.includes('일자') ||
            columnName.includes('날짜') ||
            columnName.includes('Date') ||
            columnName.includes('date')
          );
          
          if (isDateColumn) {
            // Excel 날짜 시리얼 번호인지 확인 (숫자이고 일정 범위 내)
            const numValue = parseFloat(value);
            if (!isNaN(numValue) && numValue > 40000 && numValue < 50000) {
              // Excel 날짜 시리얼 번호를 날짜로 변환
              const excelEpoch = new Date(1900, 0, 1);
              const convertedDate = new Date(excelEpoch.getTime() + (numValue - 2) * 24 * 60 * 60 * 1000);
              return convertedDate.toISOString().split('T')[0]; // YYYY-MM-DD 형식
            }
            
            // 이미 날짜 형식인지 확인
            const dateMatch = value.match(/(\d{4}-\d{2}-\d{2})/);
            if (dateMatch) {
              return dateMatch[1]; // 날짜 부분만 추출
            }
          }
          
          return value;
        };
        
        const mapped = dataRows.map((rowArr) => {
          const obj = {};
          // 상태 컬럼을 먼저 추가 (초기값: 매핑안됨)
          obj['매핑 상태'] = '매핑안됨';
          validIdx.forEach((i, idx) => {
            const columnName = filteredHeaders[idx];
            const rawValue = rowArr[i];
            obj[columnName] = formatDateValue(rawValue, columnName);
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
      // CSV 파일의 경우 여러 인코딩 시도
      const tryEncodings = async () => {
        const encodings = ['UTF-8', 'EUC-KR', 'CP949'];
        
        for (const encoding of encodings) {
          try {
            const text = await new Promise((resolve, reject) => {
              const testReader = new FileReader();
              testReader.onload = (e) => resolve(e.target.result);
              testReader.onerror = reject;
              testReader.readAsText(file, encoding);
            });
            
            // 한글이 깨지지 않는지 확인
            if (!text.includes('�') && text.includes(',')) {
              reader.onload({target: {result: text}});
              return;
            }
          } catch (err) {
            console.log(`${encoding} 인코딩 실패:`, err);
          }
        }
        
        // 모든 인코딩이 실패하면 기본 UTF-8로 읽기
        reader.readAsText(file, 'UTF-8');
      };
      
      tryEncodings();
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
        
        // 파일 경로에서 ID와 샘플번호 추출
        const pathParts = fileName.split('/');
        let historyId = null;
        let sampleNumber = null;
        let wavelength = null;
        
        // 파일명만 추출 (폴더 구조와 관계없이)
        const imageFileName = pathParts[pathParts.length - 1];
        
        // 새로운 패턴: 이력번호_s숫자_파장nm.확장자 (예: 140184300252_s1_430nm.png)
        const newPatternMatch = imageFileName.match(/^(\d+)_s(\d+)_(\d+nm)\./i);
        if (newPatternMatch) {
          historyId = newPatternMatch[1];     // 이력번호
          sampleNumber = newPatternMatch[2];  // s 뒤의 숫자
          wavelength = newPatternMatch[3];    // 파장 (430nm, 540nm 등)
        }
        
        if (historyId && sampleNumber && wavelength) {
          // 이력번호를 키로 사용
          if (!imageMap[historyId]) {
            imageMap[historyId] = {};
          }
          
          // 샘플번호를 서브키로 사용
          if (!imageMap[historyId][sampleNumber]) {
            imageMap[historyId][sampleNumber] = {};
          }
          
          // 파일 데이터를 Blob URL로 변환
          const blob = await fileObj.async('blob');
          const objectUrl = URL.createObjectURL(blob);
          
          // 파장별로 이미지 저장
          imageMap[historyId][sampleNumber][wavelength] = {
            fileName: imageFileName,
            url: objectUrl,
            wavelength: wavelength,
            sampleNumber: sampleNumber
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
    
    // 이력번호 컬럼 찾기 (새로운 데이터셋에 맞게)
    const historyIdColumn = columns.find(col => 
      col.includes('이력번호') || 
      col.includes('이력') ||
      col.toLowerCase().includes('history') ||
      col.toLowerCase().includes('id')
    );
    
    // 샘플번호 컬럼 찾기
    const sampleIdColumn = columns.find(col => 
      col.includes('샘플번호') || 
      col.includes('샘플') ||
      col.toLowerCase().includes('sample')
    );
    
    if (!historyIdColumn) {
      alert('CSV 파일에서 이력번호 컬럼을 찾을 수 없습니다.');
      return;
    }
    
    if (!sampleIdColumn) {
      alert('CSV 파일에서 샘플번호 컬럼을 찾을 수 없습니다.');
      return;
    }
    
    // 상태 컬럼과 이미지 관련 컬럼 추가
    const statusColumn = '매핑 상태';
    const imageColumns = ['이미지 파일명', '이미지 개수', '파장 정보'];
    
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
    
    // 기존 데이터 업데이트
    const updatedData = [...data];
    const existingKeys = new Set(data.map(row => `${row[historyIdColumn]}_${row[sampleIdColumn]}`));
    
    // 기존 데이터 업데이트
    updatedData.forEach(row => {
      const historyId = String(row[historyIdColumn]);
      const sampleId = String(row[sampleIdColumn]).replace(/^S/i, ''); // S1 -> 1, s2 -> 2
      
      if (imageMap[historyId] && imageMap[historyId][sampleId]) {
        const sampleImages = imageMap[historyId][sampleId];
        const wavelengths = Object.keys(sampleImages);
        const fileNames = wavelengths.map(wl => sampleImages[wl].fileName);
        
        row[statusColumn] = '매핑됨';
        row['이미지 파일명'] = fileNames.join(', ');
        row['이미지 개수'] = fileNames.length;
        row['파장 정보'] = wavelengths.join(', ');
      } else {
        row[statusColumn] = '매핑안됨';
        row['이미지 파일명'] = '';
        row['이미지 개수'] = 0;
        row['파장 정보'] = '';
      }
    });
    
    // 새로운 데이터 추가 (CSV에 없지만 이미지에는 있는 경우)
    Object.keys(imageMap).forEach(historyId => {
      Object.keys(imageMap[historyId]).forEach(sampleId => {
        const dataKey = `${historyId}_S${sampleId}`;
        if (!existingKeys.has(dataKey)) {
          const sampleImages = imageMap[historyId][sampleId];
          const wavelengths = Object.keys(sampleImages);
          const fileNames = wavelengths.map(wl => sampleImages[wl].fileName);
          
          const newRow = {};
          
          // 상태 컬럼 먼저 설정
          newRow[statusColumn] = '매핑됨';
          
          // 기존 컬럼들을 빈 값으로 초기화
          columns.forEach(col => {
            if (col === historyIdColumn) {
              newRow[col] = historyId;
            } else if (col === sampleIdColumn) {
              newRow[col] = `S${sampleId}`;
            } else {
              newRow[col] = '';
            }
          });
          
          // 이미지 정보 추가
          newRow['이미지 파일명'] = fileNames.join(', ');
          newRow['이미지 개수'] = fileNames.length;
          newRow['파장 정보'] = wavelengths.join(', ');
          
          updatedData.push(newRow);
        }
      });
    });
    
    setColumns(newColumns);
    setData(updatedData);
    
    console.log('이미지 매칭 완료:', Object.keys(imageMap).length, '개 이력번호의 이미지 처리됨');
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
