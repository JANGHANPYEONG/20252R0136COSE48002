import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 추가
import {
  Table, TableHead, TableRow, TableCell, TableBody, Checkbox, Button
} from '@mui/material';

const groupByTimestamp = (data) => {
  const groups = {};
  data.forEach(row => {
    const key = row.timestamp;
    if (!groups[key]) groups[key] = [];
    groups[key].push(row);
  });
  return groups;
};

const PredictionTableTmp = ({ data, onSelectionChange, onRowClick }) => {
  const [selectedIds, setSelectedIds] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const navigate = useNavigate(); // 추가

  const groups = groupByTimestamp(data);

  const handleGroupSelect = (timestamp) => {
    const groupRows = groups[timestamp];
    const groupIds = groupRows.map(row => row.id);

    let newSelectedIds;
    if (selectedGroup === timestamp) {
      newSelectedIds = selectedIds.filter(id => !groupIds.includes(id));
      setSelectedGroup(null);
    } else {
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
    setSelectedGroup(null);
    onSelectionChange(newSelectedIds);
  };

  const handleRowClick = (row, e) => {
    // 체크박스 클릭이 아닌 경우에만 행 클릭 처리
    if (e.target.type !== 'checkbox' && !e.target.closest('input[type="checkbox"]')) {
      if (onRowClick) {
        onRowClick(row);
      } else {
        // 기본 동작: 육류상세조회페이지로 이동
        navigate(`/meat/${row.id}`, { state: { item: row } });
      }
    }
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
                <TableCell>이력번호</TableCell>
                <TableCell>샘플번호</TableCell>
                <TableCell>부위</TableCell>
                <TableCell>딥에이징여부</TableCell>
                <TableCell>도축일자</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map(row => (
                <TableRow
                  key={row.id}
                  hover
                  onClick={(e) => handleRowClick(row, e)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>
                    <Checkbox
                      checked={selectedIds.includes(row.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleRowSelect(row.id);
                      }}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </TableCell>
                  <TableCell>{row.id}</TableCell>
                  <TableCell>{row.sampleNo}</TableCell>
                  <TableCell>{row.part}</TableCell>
                  <TableCell>{row.deepAging}</TableCell>
                  <TableCell>{row.slDate}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ))}
    </>
  );
};

export default PredictionTableTmp;
