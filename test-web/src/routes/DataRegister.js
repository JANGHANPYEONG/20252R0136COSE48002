import React, { useState, useRef, useEffect } from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import * as XLSX from 'xlsx';
import JSZip from 'jszip';
import style from './style/dashboardstyle';
import DataListWithURL from '../components/DataListWithURL';
import uploadFiles from '../API/add/uploadToS3'; // 통합 업로드 API import

const navy = '#0F3659';

const DataRegister = () => {
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [csvLoading, setCsvLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState(''); // 성공 메시지 상태
  const [uploadedZipFile, setUploadedZipFile] = useState(null); // ZIP 파일 또는 폴더 상태 추가

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

  const handleRegister = async () => {
    try {
      // 1. 데이터 존재 여부 확인
      if (!data || data.length === 0) {
        alert('업로드할 데이터가 없습니다. 먼저 CSV 파일을 업로드해주세요.');
        return;
      }

      // 2. 이미지 파일 존재 여부 확인
      if (!uploadedZipFile) {
        alert('이미지 파일이 업로드되지 않았습니다. 먼저 ZIP 파일 또는 폴더를 업로드해주세요.');
        return;
      }

      // ZIP 파일 형태인지 확인
      if (!(uploadedZipFile instanceof File)) {
        alert('업로드된 이미지가 올바른 형식이 아닙니다. 다시 업로드해주세요.');
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
      
      // 4. 설정에 따른 파일 업로드 (서버/S3 자동 선택)
      const result = await uploadFiles(data, columns, uploadedZipFile);
      
      if (result.success) {
        // 성공 시 상세 정보와 함께 알림
        const successDetails = result.data 
          ? `\n- 데이터 ${result.data.dataCount || 0}건 등록\n- CSV: ${result.data.csvPath || 'N/A'}\n- 이미지: ${result.data.imagePath || 'N/A'}`
          : '';
        
        alert(`데이터 등록이 성공적으로 완료되었습니다!${successDetails}`);
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
          rowsArray = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
          
          // 빈 행 제거
          rowsArray = rowsArray.filter(row => row.some(cell => cell !== ''));
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
        
        // Excel 날짜 시리얼 번호를 날짜로 변환하는 함수
        const excelDateToJS = (serial) => {
          // Excel 1900 시스템: 1900년 1월 1일 = 1
          // 하지만 실제로는 1899년 12월 31일을 0으로 계산해야 정확함
          const excelBaseDate = new Date(1900, 0, 1); // 1900년 1월 1일
          const millisecondsPerDay = 24 * 60 * 60 * 1000;
          
          // Excel 시리얼 번호에서 1을 빼고 계산 (Excel이 1부터 시작하므로)
          const resultDate = new Date(excelBaseDate.getTime() + (serial - 1) * millisecondsPerDay);
          
          return resultDate;
        };
        
        // 특정 날짜 컬럼인지 확인하는 함수
        const isSpecificDateColumn = (columnName) => {
          if (!columnName) return false;
          const name = columnName.toString();
          return name.includes('도축일자') || 
                 name.includes('제조(가공)일자') || 
                 name.includes('소비기한');
        };
        
        const mapped = dataRows.map((rowArr) => {
          const obj = {};
          // 상태 컬럼을 먼저 추가 (초기값: 매핑안됨)
          obj['매핑 상태'] = '매핑안됨';
          validIdx.forEach((i, idx) => {
            const columnName = filteredHeaders[idx];
            let cellValue = rowArr[i] || '';
            
            // 특정 날짜 컬럼이고 숫자(시리얼 번호)인 경우 날짜로 변환
            if (isSpecificDateColumn(columnName)) {
              // 문자열을 숫자로 변환 시도
              const numValue = parseFloat(cellValue);
              if (!isNaN(numValue) && numValue > 1 && numValue < 100000) {
                try {
                  const date = excelDateToJS(numValue);
                  cellValue = date.toISOString().split('T')[0]; // YYYY-MM-DD 형식
                  console.log(`날짜 변환: ${columnName} ${numValue} -> ${cellValue}`);
                } catch (e) {
                  console.error('날짜 변환 오류:', e);
                  cellValue = cellValue.toString();
                }
              }
            }
            
            obj[columnName] = cellValue;
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

  // 폴더 업로드 처리
  const handleFolderImageUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files || files.length === 0) return;
    
    setImageLoading(true);
    
    try {
      console.log('폴더 처리:', files.length, '개 파일');
      
      // 1. 이미지 매핑 처리
      await handleFolderFiles(files);
      
      // 2. 폴더 파일들을 ZIP으로 압축
      console.log('폴더를 ZIP 파일로 압축 중...');
      const zipFile = await createZipFromFiles(files);
      
      // 3. ZIP 파일을 상태에 저장
      setUploadedZipFile(zipFile);
      
      console.log('폴더 처리 및 ZIP 생성 완료');
    } catch (error) {
      console.error('폴더 처리 오류:', error);
      alert('폴더 처리 중 오류가 발생했습니다.');
      setUploadedZipFile(null); // 오류 시 상태 초기화
    } finally {
      setImageLoading(false);
    }
  };

  // 폴더 파일들을 ZIP 파일로 압축하는 함수
  const createZipFromFiles = async (files) => {
    const zip = new JSZip();
    
    // 루트 폴더명 추출 (첫 번째 파일의 경로에서)
    const firstFilePath = files[0].webkitRelativePath || files[0].name;
    const rootFolderName = firstFilePath.split('/')[0] || 'folder';
    
    console.log(`ZIP 파일 생성: 루트 폴더명 = ${rootFolderName}`);
    
    // 모든 파일을 ZIP에 추가
    for (const file of files) {
      const relativePath = file.webkitRelativePath || file.name;
      console.log(`ZIP에 파일 추가: ${relativePath}`);
      zip.file(relativePath, file);
    }
    
    // ZIP 파일 생성
    const zipBlob = await zip.generateAsync({
      type: 'blob',
      compression: 'DEFLATE',
      compressionOptions: {
        level: 6
      }
    });
    
    // File 객체로 변환 (원본 ZIP 파일과 동일한 형태)
    const zipFile = new File([zipBlob], `${rootFolderName}.zip`, {
      type: 'application/zip'
    });
    
    console.log(`ZIP 파일 생성 완료: ${zipFile.name} (${(zipFile.size / 1024 / 1024).toFixed(2)} MB)`);
    
    return zipFile;
  };

  // 폴더 파일들 처리
  const handleFolderFiles = async (files) => {
    try {
      const imageMap = {};
      
      // 모든 파일을 순회
      for (const file of files) {
        // 이미지 파일 확인
        const isImage = /\.(jpg|jpeg|png|gif|bmp)$/i.test(file.name);
        if (!isImage) continue;
        
        // 파일 경로 분석: 관리번호/부위폴더/이미지파일명
        const fullPath = file.webkitRelativePath || file.name;
        const pathParts = fullPath.split('/');
        
        // 최소 3단계 경로 필요: 관리번호폴더/부위폴더/파일명
        if (pathParts.length < 3) continue;
        
        const managementNumber = pathParts[pathParts.length - 3]; // 관리번호 (예: 149119100857)
        const partFolder = pathParts[pathParts.length - 2];       // 부위 폴더 (예: S1)
        const fileName = pathParts[pathParts.length - 1];         // 파일명
        
        // 부위 폴더에서 샘플 번호 추출 (S1 -> 1)
        const sampleMatch = partFolder.match(/^S(\d+)$/i);
        if (!sampleMatch) continue;
        
        const sampleNumber = sampleMatch[1];
        
        // 파일명에서 파장 정보 추출 (예: 140119100857_s1_430nm.png)
        const wavelengthMatch = fileName.match(/(\d+nm)/i);
        if (!wavelengthMatch) continue;
        
        const wavelength = wavelengthMatch[1];
        
        // 이미지 맵 구성
        if (!imageMap[managementNumber]) {
          imageMap[managementNumber] = {};
        }
        
        if (!imageMap[managementNumber][sampleNumber]) {
          imageMap[managementNumber][sampleNumber] = {};
        }
        
        // 파일을 Blob URL로 변환
        const objectUrl = URL.createObjectURL(file);
        
        // 파장별로 이미지 저장
        imageMap[managementNumber][sampleNumber][wavelength] = {
          fileName: fileName,
          url: objectUrl,
          wavelength: wavelength,
          sampleNumber: sampleNumber,
          file: file
        };
        
        console.log(`이미지 매핑: ${managementNumber} / S${sampleNumber} / ${wavelength} -> ${fileName}`);
      }
      
      // 기존 데이터와 매칭
      await matchImagesWithData(imageMap);
      
    } catch (error) {
      console.error('폴더 파일 처리 오류:', error);
      throw error;
    }
  };

  // ZIP 파일 처리 (단순화 버전)
  const handleZipFile = async (zipFile) => {
    try {
      console.log('=== ZIP 파일 처리 시작 ===');
      const zip = new JSZip();
      const zipData = await zip.loadAsync(zipFile);
      const imageMap = {};
      
      console.log('ZIP 파일 내용:', Object.keys(zipData.files));
      
      // ZIP 파일 내의 모든 파일을 순회
      for (const [fileName, fileObj] of Object.entries(zipData.files)) {
        if (fileObj.dir) {
          console.log(`폴더 건너뛰기: ${fileName}`);
          continue;
        }
        
        // 이미지 파일 확인
        const isImage = /\.(jpg|jpeg|png|gif|bmp)$/i.test(fileName);
        if (!isImage) {
          console.log(`이미지가 아님: ${fileName}`);
          continue;
        }
        
        console.log(`처리 중인 이미지: ${fileName}`);
        
        // 파일 경로 분석
        const pathParts = fileName.split('/').filter(part => part.length > 0);
        console.log(`경로 분석: ${JSON.stringify(pathParts)}`);
        
        let managementNumber = null;
        let sampleNumber = null;
        let wavelength = null;
        
        // 방법 1: 폴더 구조 분석 (관리번호/S1/파일명.png)
        if (pathParts.length >= 3) {
          const folder1 = pathParts[pathParts.length - 3]; // 관리번호 폴더
          const folder2 = pathParts[pathParts.length - 2]; // 부위 폴더 (S1, S2, ...)
          const imageName = pathParts[pathParts.length - 1]; // 파일명
          
          // 관리번호는 숫자여야 함
          if (/^\d+$/.test(folder1)) {
            // 부위 폴더는 S1, S2 형태여야 함
            const sampleMatch = folder2.match(/^S(\d+)$/i);
            if (sampleMatch) {
              // 파일명에서 파장 추출
              const wavelengthMatch = imageName.match(/(\d+nm)/i);
              if (wavelengthMatch) {
                managementNumber = folder1;
                sampleNumber = sampleMatch[1];
                wavelength = wavelengthMatch[1];
                console.log(`✅ 폴더 구조 인식: ${managementNumber}/S${sampleNumber}/${wavelength}`);
              }
            }
          }
        }
        
        // 방법 2: 파일명 패턴 분석 (숫자_s숫자_파장nm.확장자)
        if (!managementNumber) {
          const imageName = pathParts[pathParts.length - 1];
          const patternMatch = imageName.match(/^(\d+)_s(\d+)_(\d+nm)\./i);
          if (patternMatch) {
            managementNumber = patternMatch[1];
            sampleNumber = patternMatch[2];
            wavelength = patternMatch[3];
            console.log(`✅ 파일명 패턴 인식: ${managementNumber}/S${sampleNumber}/${wavelength}`);
          }
        }
        
        // 인식 실패 시 로그
        if (!managementNumber || !sampleNumber || !wavelength) {
          console.log(`❌ 인식 실패: ${fileName} (관리번호=${managementNumber}, 샘플=${sampleNumber}, 파장=${wavelength})`);
          continue;
        }
        
        // 이미지 맵 구성
        if (!imageMap[managementNumber]) {
          imageMap[managementNumber] = {};
          console.log(`새 관리번호 생성: ${managementNumber}`);
        }
        
        if (!imageMap[managementNumber][sampleNumber]) {
          imageMap[managementNumber][sampleNumber] = {};
          console.log(`새 샘플번호 생성: ${managementNumber}/S${sampleNumber}`);
        }
        
        // 파일 데이터를 Blob URL로 변환
        const blob = await fileObj.async('blob');
        const objectUrl = URL.createObjectURL(blob);
        
        // 파장별로 이미지 저장
        imageMap[managementNumber][sampleNumber][wavelength] = {
          fileName: pathParts[pathParts.length - 1],
          url: objectUrl,
          wavelength: wavelength,
          sampleNumber: sampleNumber
        };
        
        console.log(`✅ 이미지 저장 완료: ${managementNumber}/S${sampleNumber}/${wavelength}`);
      }
      
      console.log('=== 최종 이미지 맵 ===');
      console.log('인식된 관리번호들:', Object.keys(imageMap));
      Object.keys(imageMap).forEach(mgmtNum => {
        console.log(`관리번호 ${mgmtNum}의 샘플들:`, Object.keys(imageMap[mgmtNum]));
      });
      console.log('전체 이미지 맵:', imageMap);
      
      // 기존 데이터와 매칭
      await matchImagesWithData(imageMap);
      
    } catch (error) {
      console.error('ZIP 파일 처리 오류:', error);
      throw error;
    }
  };

  // 이미지와 데이터 매칭 (간단한 버전)
  const matchImagesWithData = async (imageMap) => {
    if (!columns.length) {
      alert('먼저 XLSX 파일을 업로드해주세요.');
      return;
    }
    
    console.log('=== 매칭 시작 ===');
    console.log('이미지 맵 키들:', Object.keys(imageMap));
    console.log('이미지 맵 전체 구조:');
    Object.keys(imageMap).forEach(mgmtNum => {
      console.log(`  관리번호 ${mgmtNum}:`);
      Object.keys(imageMap[mgmtNum]).forEach(sampleNum => {
        const wavelengths = Object.keys(imageMap[mgmtNum][sampleNum]);
        console.log(`    샘플 ${sampleNum}: [${wavelengths.join(', ')}]`);
      });
    });
    console.log('기존 데이터:', data);
    console.log('컬럼들:', columns);
    
    // 관리번호와 샘플번호 컬럼 찾기
    const managementNumberColumn = columns.find(col => 
      col.includes('관리번호') || col.includes('이력번호') || col.includes('이력')
    );
    
    const sampleIdColumn = columns.find(col => 
      col.includes('샘플번호') || col.includes('샘플') || col.includes('부위번호') || col.includes('부위')
    );
    
    if (!managementNumberColumn || !sampleIdColumn) {
      alert(`매칭에 필요한 컬럼을 찾을 수 없습니다.\n관리번호 컬럼: ${managementNumberColumn}\n샘플번호 컬럼: ${sampleIdColumn}`);
      return;
    }
    
    console.log(`매칭 기준 컬럼: ${managementNumberColumn}, ${sampleIdColumn}`);
    
    // 상태 컬럼과 이미지 관련 컬럼 추가
    const statusColumn = '매핑 상태';
    const imageColumns = ['이미지 파일명', '이미지 개수', '파장 정보'];
    
    let newColumns = [...columns];
    if (!newColumns.includes(statusColumn)) {
      newColumns = [statusColumn, ...newColumns];
    }
    imageColumns.forEach(col => {
      if (!newColumns.includes(col)) {
        newColumns.push(col);
      }
    });
    
    // 기존 데이터 복사 및 매핑 상태 초기화
    const updatedData = data.map(row => {
      const newRow = { ...row };
      newRow[statusColumn] = '매핑안됨';
      newRow['이미지 파일명'] = '';
      newRow['이미지 개수'] = 0;
      newRow['파장 정보'] = '';
      return newRow;
    });
    
    let matchedCount = 0;
    
    // 각 데이터 행에 대해 이미지 찾기
    updatedData.forEach((row, index) => {
      const managementNumber = String(row[managementNumberColumn] || '').trim();
      const originalSampleId = String(row[sampleIdColumn] || '').trim();
      const sampleId = originalSampleId.replace(/^S/i, ''); // S1 -> 1
      
      console.log(`[행 ${index}] 매칭 시도: 관리번호="${managementNumber}", 원본샘플="${originalSampleId}", 변환샘플="${sampleId}"`);
      
      // 이미지 맵에서 해당 관리번호와 샘플번호로 이미지 찾기
      if (imageMap[managementNumber] && imageMap[managementNumber][sampleId]) {
        const sampleImages = imageMap[managementNumber][sampleId];
        const wavelengths = Object.keys(sampleImages);
        const fileNames = wavelengths.map(wl => sampleImages[wl].fileName);
        
        row[statusColumn] = '매핑됨';
        row['이미지 파일명'] = fileNames.join(', ');
        row['이미지 개수'] = fileNames.length;
        row['파장 정보'] = wavelengths.join(', ');
        
        matchedCount++;
        console.log(`✅ 매칭 성공: ${managementNumber}/S${sampleId} - ${fileNames.length}개 이미지`);
      } else {
        console.log(`❌ 매칭 실패: ${managementNumber}/S${sampleId} (이미지 없음)`);
      }
    });
    
    // 상태 업데이트
    setColumns(newColumns);
    setData(updatedData);
    
    console.log('=== 매칭 완료 ===');
    // alert 대신 자동으로 사라지는 메시지 사용
    showSuccessMessage(`매칭 완료! 총 ${data.length}개 데이터 중 ${matchedCount}개 매칭됨`);
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
              'XLSX 불러오기'
            )}
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              const input = document.createElement('input');
              input.type = 'file';
              input.accept = '.zip';
              input.addEventListener('change', handleZipImageUpload);
              input.click();
            }}
            disabled={csvLoading || imageLoading}
            sx={{
              backgroundColor: navy,
              '&:hover': { backgroundColor: '#0a2a4a' },
            }}
          >
            {imageLoading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              '이미지 불러오기 (ZIP)'
            )}
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              const folderInput = document.createElement('input');
              folderInput.type = 'file';
              folderInput.webkitdirectory = true;
              folderInput.multiple = true;
              folderInput.addEventListener('change', handleFolderImageUpload);
              folderInput.click();
            }}
            disabled={csvLoading || imageLoading}
            sx={{
              backgroundColor: navy,
              '&:hover': { backgroundColor: '#0a2a4a' },
            }}
          >
            {imageLoading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              '이미지 불러오기 (폴더)'
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
