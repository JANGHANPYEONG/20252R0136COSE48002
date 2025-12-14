import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';

const navy = '#0F3659';

const DataList = ({ columns, data, title }) => {
  // 통계 계산
  const totalCount = data.length;
  const mappedCount = data.filter(row => row['매핑 상태'] === '매핑됨').length;
  const unmappedCount = totalCount - mappedCount; // 매핑됨이 아닌 모든 것을 매핑안됨으로 처리

  return (
    <Box sx={{ marginTop: 2 }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: 2,
        gap: 3
      }}>
        <h3 style={{ margin: 0, color: navy }}>{title}</h3>
        <Box sx={{ 
          display: 'flex', 
          gap: 2,
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '17px', color: '#666' }}>
            총 <strong style={{ color: navy }}>{totalCount}</strong>
          </span>
          <span style={{ fontSize: '17px', color: '#666' }}>|</span>
          <span style={{ fontSize: '17px', color: '#28a745' }}>
            매핑됨 <strong>{mappedCount}</strong>
          </span>
          <span style={{ fontSize: '17px', color: '#666' }}>|</span>
          <span style={{ fontSize: '17px', color: '#dc3545' }}>
            매핑안됨 <strong>{unmappedCount}</strong>
          </span>
        </Box>
      </Box>
      <TableContainer 
        component={Paper} 
        sx={{ 
          height: 'calc(100vh - 250px)', // 화면 높이에서 상단 여백을 뺀 높이
          minHeight: '600px', // 최소 높이 보장
          border: '1px solid #e0e0e0',
          overflow: 'auto' // 스크롤 가능
        }}
      >
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((col, idx) => (
                <TableCell
                  key={idx}
                  sx={{ 
                    backgroundColor: '#f5f5f5', 
                    fontWeight: 'bold', 
                    color: navy,
                    border: '1px solid #e0e0e0',
                    padding: '12px 16px',
                    fontSize: '14px',
                    textAlign: 'center', // 모든 헤더를 가운데 정렬
                    // 매핑 상태와 이미지 개수 컬럼에 고정 너비 적용
                    ...(col === '매핑 상태' && {
                      width: '140px',
                      minWidth: '140px',
                      maxWidth: '140px'
                    }),
                    ...(col === '이미지 개수' && {
                      width: '100px',
                      minWidth: '100px',
                      maxWidth: '100px'
                    })
                  }}
                >
                  {col}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.length > 0 ? (
              data.map((row, ridx) => (
                <TableRow 
                  key={ridx}
                  sx={{
                    '&:nth-of-type(odd)': {
                      backgroundColor: '#fafafa',
                    },
                    '&:hover': {
                      backgroundColor: '#f0f0f0',
                    },
                  }}
                >
                  {columns.map((col, cidx) => {
                    const cell = row[col] ?? '';
                    
                    // 이미지/일련번호 컬럼 클릭 시 팝업
                    if ((col === '이미지 파일명' || col === '이미지 파일명' || col === '일련번호 파일명') && cell) {
                      const urlKey = col.includes('이미지') ? '이미지_URL' || '이미지URL' : '일련번호URL';
                      const url = row[urlKey] || row['이미지URL'];
                      return (
                        <TableCell
                          key={cidx}
                          sx={{ 
                            color: navy, 
                            cursor: 'pointer', 
                            textDecoration: 'underline',
                            border: '1px solid #e0e0e0',
                            padding: '12px 16px',
                            fontSize: '13px'
                          }}
                          onClick={() => url && window.open(url, '_blank', 'width=600,height=400')}
                        >
                          {cell}
                        </TableCell>
                      );
                    }
                    
                    return (
                      <TableCell 
                        key={cidx}
                        sx={{
                          border: '1px solid #e0e0e0',
                          padding: '12px 16px',
                          fontSize: '13px',
                          // 매핑 상태와 이미지 개수 컬럼 스타일
                          ...(col === '매핑 상태' && {
                            width: '140px',
                            minWidth: '140px',
                            maxWidth: '140px',
                            textAlign: 'center',
                            fontWeight: '500',
                            whiteSpace: 'nowrap'
                          }),
                          ...(col === '이미지 개수' && {
                            width: '100px',
                            minWidth: '100px',
                            maxWidth: '100px',
                            textAlign: 'center',
                            fontWeight: '500'
                          })
                        }}
                      >
                        {col === '매핑 상태' ? (
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold',
                            backgroundColor: cell === '매핑됨' ? '#28a745' : '#dc3545',
                            color: 'white'
                          }}>
                            {cell || '매핑안됨'}
                          </span>
                        ) : (cell || '-')}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell 
                  colSpan={columns.length} 
                  align="center"
                  sx={{
                    border: '1px solid #e0e0e0',
                    padding: '24px',
                    fontSize: '14px',
                    color: '#666'
                  }}
                >
                  데이터가 없습니다.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default DataList;