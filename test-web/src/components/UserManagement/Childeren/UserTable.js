import React from 'react';
import { format } from 'date-fns';
import { IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import UserTypeEditCell from './UserTypeEditCell';

const UserTable = (
  handleDeleteConfirmShow,
  setAllUsers,
  handleSnackbarShow
) => [
  { field: 'name', headerName: '이름', width: 100 },
  { field: 'userId', headerName: '아이디', width: 250 },
  {
    field: 'type',
    headerName: '권한',
    width: 200,
    renderCell: (params) => (
      <UserTypeEditCell
        id={params.id}
        field={params.field}
        value={params.value}
        api={params.api}
        setAllUsers={setAllUsers}
        handleSnackbarShow={handleSnackbarShow}
      />
    ),
  },
  { field: 'company', headerName: '회사', width: 120 },
  {
    field: 'createdAt',
    headerName: '회원가입 날짜',
    width: 240,
    renderCell: (params) => {
      const createdAt = params.row.createdAt;
      if (createdAt) {
        const parsedDate = new Date(createdAt);
        return format(parsedDate, 'y년 M월 d일 a h시 m분');
      }
      return '';
    },
  },
  {
    field: 'actions',
    headerName: '',
    width: 120,
    renderCell: (params) => (
      <div>
        <IconButton onClick={() => handleDeleteConfirmShow(params.row)}>
          <DeleteIcon />
        </IconButton>
      </div>
    ),
  },
];

export default UserTable;
