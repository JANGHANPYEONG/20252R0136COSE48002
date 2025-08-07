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

import React, { useState } from 'react';
import {
  Table, TableHead, TableRow, TableCell, TableBody, Checkbox, Button
} from '@mui/material';

// timestamp 기준 그룹화 함수
const groupByTimestamp = (data) => {
  const groups = {};
  data.forEach(row => {
    const key = row.timestamp;
    if (!groups[key]) groups[key] = [];
    groups[key].push(row);
  });
  return groups;
};

const PredictionTable = ({ data, onSelectionChange, onRowClick }) => {
  const [selectedIds, setSelectedIds] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);

  const groups = groupByTimestamp(data);

  const handleGroupSelect = (timestamp) => {
    const groupRows = groups[timestamp];
    const groupIds = groupRows.map(row => row.id);

    let newSelectedIds;
    if (selectedGroup === timestamp) {
      // 그룹 선택 해제
      newSelectedIds = selectedIds.filter(id => !groupIds.includes(id));
      setSelectedGroup(null);
    } else {
      // 그룹 선택
      newSelectedIds = [...selectedIds, ...groupIds.filter(id => !selectedIds.includes(id))];
      setSelectedGroup(timestamp);
    }

    setSelectedIds(newSelectedIds);
    onSelectionChange(newSelectedIds);
  };

  const handleRowSelect = (id) => {
    const newSelectedIds = selectedIds.includes(id)
      ? selectedIds.filter(item => item !== id)
      : [...selectedIds, id];
    setSelectedIds(newSelectedIds);
    setSelectedGroup(null);  // 개별 선택 시 그룹 선택 해제
    onSelectionChange(newSelectedIds);
  };

  return (
    <>
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
                <TableCell>ID</TableCell>
                <TableCell>스펙트럼</TableCell>
                <TableCell>파장</TableCell>
                <TableCell>날짜</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map(row => {
                const isPredicted = !!row.prediction;

                return (
                    <TableRow
                        key={row.id}
                        hover={isPredicted}
                        onClick={() => isPredicted && onRowClick?.(row)}
                        sx={{
                            cursor: isPredicted ? 'pointer' : 'default',
                            backgroundColor : isPredicted ? 'inherit' : '#f5f5f5',
                            opacity : isPredicted ? 1 : 0.6,
                        }}
                    >
                  <TableCell>
                    <Checkbox
                      checked={selectedIds.includes(row.id)}
                      onChange={() => handleRowSelect(row.id)}
                    />
                  </TableCell>
                  <TableCell>{row.id}</TableCell>
                  <TableCell>{row.spectrum}</TableCell>
                  <TableCell>{row.wavelength}</TableCell>
                  <TableCell>{row.date}</TableCell>
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
