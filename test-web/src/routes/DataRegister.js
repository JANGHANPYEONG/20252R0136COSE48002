import React, { useState, useRef } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
} from '@mui/material';
import Papa from 'papaparse';

const DataRegister = () => {
  const [csvData, setCsvData] = useState({ headers: [], rows: [] });
  const fileInputRef = useRef(null);

  const handleLoadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const buffer = evt.target.result;
      let text;
      // 지원 가능한 인코딩 시도: windows-949 -> euc-kr -> utf-8
      try {
        text = new TextDecoder('windows-949').decode(buffer);
      } catch {
        try {
          text = new TextDecoder('euc-kr').decode(buffer);
        } catch {
          text = new TextDecoder('utf-8').decode(buffer);
        }
      }
      // BOM(Byte Order Mark) 제거
      if (text.charCodeAt(0) === 0xFEFF) {
        text = text.slice(1);
      }

      // 문자열 데이터를 PapaParse로 파싱
      Papa.parse(text, {
        header: false,
        skipEmptyLines: true,
        encoding : "UTF-8",
        complete: (results) => {
          const data = results.data;
          const [headers, ...rows] = data;
          setCsvData({ headers, rows });
        },
        error: (err) => {
          console.error('CSV 파싱 오류:', err);
          alert('CSV 파싱 중 오류가 발생했습니다.');
        }
      });
    };
    // 바이너리로 읽어들여 TextDecoder로 디코딩
    reader.readAsArrayBuffer(file);
    // 동일 파일 재선택 허용
    e.target.value = null;
  };

  const { headers, rows } = csvData;

  return (
    <Container maxWidth="lg" sx={{ mt: 10, width: '100%' }}>
      <Typography variant="h4" sx={{ fontWeight: 600, color: '#151D48', mb: 4 }}>
        데이터 등록
      </Typography>

      {/* 숨겨진 파일 입력 */}
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".csv"
        onChange={handleFileChange}
      />

      <Box sx={{ mb: 3 }}>
        <Button variant="contained" onClick={handleLoadClick}>
          CSV 불러오기
        </Button>
      </Box>

      {/* 미리보기 영역: 고정 크기 박스, 스크롤 */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>미리보기</Typography>
        {headers.length > 0 ? (
          <TableContainer sx={{ width: '100%', maxHeight: 400, overflowY: 'auto' }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  {headers.map((h, i) => (
                    <TableCell key={i}>{h}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row, ri) => (
                  <TableRow key={ri}>
                    {row.map((cell, ci) => (
                      <TableCell key={ci}>{cell}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography>불러온 데이터가 없습니다.</Typography>
        )}
      </Box>

      {/* 등록하기 버튼 (API 미연결) */}
      <Button variant="contained" color="primary" disabled={rows.length === 0}>
        등록하기
      </Button>
    </Container>
  );
};

export default DataRegister;