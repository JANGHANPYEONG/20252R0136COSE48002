//데이터 예시 구조
/*
const data = [
  {
    id: 'M001',
    spectrum: '123,124,...',
    wavelength: '650nm',
    timestamp: '2025-08-07T10:15:00',
    date: '2025-08-07',
  },
  {
    id: 'M002',
    spectrum: '...',
    timestamp: '2025-08-07T10:15:00',
    date: '2025-08-07',
  },
  {
    id: 'M003',
    timestamp: '2025-08-07T11:20:00',
    date: '2025-08-07',
  },
]
*/

import React, { useState, useEffect } from 'react';
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Checkbox,
  Button,
  Box,
  Typography,
} from '@mui/material';

// timestamp 기준 그룹화 함수
const groupByTimestamp = (data) => {
  const groups = {};
  data.forEach((row) => {
    const key = row.timestamp;
    if (!groups[key]) groups[key] = [];
    groups[key].push(row);
  });
  return groups;
};

const PredictionTable = ({ data, onSelectionChange, onRowClick, selectedRows = [] }) => {
  const [selectedIds, setSelectedIds] = useState(selectedRows.map(row => typeof row === 'string' ? row : row.id));
  const [selectedGroup, setSelectedGroup] = useState(null);

  // selectedRows prop이 변경될 때 selectedIds 동기화
  useEffect(() => {
    const newSelectedIds = selectedRows.map(row => typeof row === 'string' ? row : row.id);
    setSelectedIds(newSelectedIds);
  }, [selectedRows]);

  const groups = groupByTimestamp(data);
  const allDataIds = data.map((row) => row.id);
  const isAllSelected =
    allDataIds.length > 0 && allDataIds.every((id) => selectedIds.includes(id));

  // 전체 선택/해제 핸들러
  const handleSelectAll = () => {
    let newSelectedIds;
    if (isAllSelected) {
      // 전체 해제
      newSelectedIds = [];
    } else {
      // 전체 선택
      newSelectedIds = [...allDataIds];
    }
    setSelectedIds(newSelectedIds);
    setSelectedGroup(null);
    onSelectionChange(newSelectedIds);
  };

  const handleGroupSelect = (timestamp) => {
    const groupRows = groups[timestamp];
    const groupIds = groupRows.map((row) => row.id);

    let newSelectedIds;
    if (selectedGroup === timestamp) {
      // 그룹 선택 해제
      newSelectedIds = selectedIds.filter((id) => !groupIds.includes(id));
      setSelectedGroup(null);
    } else {
      // 그룹 선택
      newSelectedIds = [
        ...selectedIds,
        ...groupIds.filter((id) => !selectedIds.includes(id)),
      ];
      setSelectedGroup(timestamp);
    }

    setSelectedIds(newSelectedIds);
    onSelectionChange(newSelectedIds);
  };

  const handleRowSelect = (id) => {
    const newSelectedIds = selectedIds.includes(id)
      ? selectedIds.filter((item) => item !== id)
      : [...selectedIds, id];
    setSelectedIds(newSelectedIds);
    setSelectedGroup(null); // 개별 선택 시 그룹 선택 해제
    onSelectionChange(newSelectedIds);
  };

  return (
    <>
      {/* 전체 선택 체크박스 */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, mt: 2 }}>
        <Checkbox checked={isAllSelected} onChange={handleSelectAll} />
        <Typography variant="body2" sx={{ ml: 1 }}>
          전체 선택 ({selectedIds.length}/{allDataIds.length})
        </Typography>
      </Box>

      {Object.entries(groups).map(([timestamp, rows]) => (
        <div key={timestamp}>
          <Button
            variant={selectedGroup === timestamp ? 'contained' : 'outlined'}
            onClick={() => handleGroupSelect(timestamp)}
            sx={{ mt: 2 }}
          >
            {timestamp} 그룹 선택
          </Button>

          <Table size="small" sx={{ mt: 1 }}>
            <TableHead>
              <TableRow>
                <TableCell>선택</TableCell>
                <TableCell>이력번호</TableCell>
                <TableCell>부위</TableCell>
                <TableCell>딥에이징여부</TableCell>
                <TableCell>도축일자</TableCell>
                <TableCell>가공일자</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => {
                const isPredicted = !!row.prediction;

                return (
                  <TableRow
                    key={row.id}
                    onClick={() => isPredicted && onRowClick?.(row)}
                    sx={{
                      backgroundColor: isPredicted ? 'inherit' : '#f5f5f5',
                      opacity: isPredicted ? 1 : 0.6,
                      cursor: isPredicted ? 'pointer' : 'default',
                      '&:hover': isPredicted
                        ? { backgroundColor: '#f0f0f0' }
                        : {},
                    }}
                  >
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        checked={selectedIds.includes(row.id)}
                        onChange={() => handleRowSelect(row.id)}
                      />
                    </TableCell>
                    <TableCell>{row.traceNum || row.id}</TableCell>
                    <TableCell>{row.part}</TableCell>
                    <TableCell>{row.isDeepAged}</TableCell>
                    <TableCell>{row.butcheryDate}</TableCell>
                    <TableCell>{row.processDate || '-'}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      ))}
    </>
  );
};

export default PredictionTable;
