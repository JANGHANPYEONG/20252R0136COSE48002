import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  CircularProgress,
} from '@mui/material';
import * as XLSX from 'xlsx';
import style from './style/dashboardstyle';
import DataList from '../components/DataList';

const navy = '#0F3659';

const DataRegister = () => {
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);

  const handleLoadClick = () => fileInputRef.current?.click();
  const handleImageClick = () => imageInputRef.current?.click();

  const handleRegister = async () => {
    const payload = data;
    console.log('전송할 payload:', payload);
    // TODO: 실제 API 호출
    try {
      setLoading(true);
      const res = await fetch('/api/data/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: payload }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      alert('데이터 등록 성공!');
      setColumns([]);
      setData([]);
    } catch (err) {
      console.error('등록 오류:', err);
      alert('데이터 등록에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const reader = new FileReader();
    reader.onload = (evt) => {
      const buffer = evt.target.result;
      const workbook = XLSX.read(buffer, { type: 'array' });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rowsArray = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
      if (!rowsArray.length) {
        setColumns([]);
        setData([]);
        setLoading(false);
        return;
      }
      const headerRow = rowsArray[1].map(String);
      const dataRows = rowsArray.slice(2).filter((r) => r.some((cell) => cell !== ''));
      setColumns(headerRow);
      const mappedData = dataRows.map((rowArr) => {
        const obj = {};
        headerRow.forEach((h, idx) => {
          obj[h] = rowArr[idx];
        });
        return obj;
      });
      console.log('Parsed headers:', headerRow);
      console.log('Parsed data:', mappedData);
      setData(mappedData);
      setLoading(false);
    };
    reader.readAsArrayBuffer(file);
    e.target.value = null;
  };

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    // index 추출: (숫자) 패턴
    const imageMap = files.reduce((map, file) => {
      const match = file.name.match(/\((\d+)\)/);
      if (match) map[match[1]] = file.name;
      return map;
    }, {});

    // 이미지 컬럼 추가
    const imageColumn = '이미지 파일명';
    if (!columns.includes(imageColumn)) {
      setColumns((prev) => [...prev, imageColumn]);
    }
    // data에 이미지 파일명 매핑
    setData((prev) => {
      const indexKey = columns[0]; // 인덱스 컬럼은 첫 번째 컬럼으로 가정
      return prev.map((row) => ({
        ...row,
        [imageColumn]: imageMap[row[indexKey]] || ''
      }));
    });
    e.target.value = null;
  };

  return (
    <div style={{ overflow: 'auto', width: '100%', marginTop: '100px', paddingLeft: '30px', paddingRight: '20px', height: '100%' }}>
      {/* 페이지 제목 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 600, color: navy, fontSize: '30px' }}>
          데이터 등록
        </Typography>
      </Box>

      {/* 숨겨진 파일 입력 */}
      <input
        type="file"
        accept=".xlsx"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      {/* 숨겨진 이미지 폴더 입력 */}
      <input
        type="file"
        webkitdirectory="true"
        multiple
        accept="image/*"
        ref={imageInputRef}
        style={{ display: 'none' }}
        onChange={handleImageChange}
      />

      {/* 버튼 영역 */}
      <Box sx={{ ...style.fixedTab, display: 'flex', alignItems: 'center', gap: 2, pt: 2 }}>
        {/* 왼쪽 버튼 그룹 */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            disabled={loading}
            onClick={handleLoadClick}
            sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
          >
            {loading ? <CircularProgress size={20} color="inherit" /> : '데이터 불러오기'}
          </Button>
          <Button
            variant="contained"
            disabled={loading}
            onClick={handleImageClick}
            sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
          >
            사진 불러오기
          </Button>
        </Box>

        {/* 오른쪽 등록 버튼 */}
        <Button
          variant="contained"
          disabled={!data.length || loading}
          onClick={handleRegister}
          sx={{ marginLeft: 'auto', backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
        >
          {loading ? <CircularProgress size={20} color="inherit" /> : '데이터 등록'}
        </Button>
      </Box>

      {/* 미리보기 리스트 */}
      <DataList title="미리보기" columns={columns} data={data} />
    </div>
  );
};

export default DataRegister;
