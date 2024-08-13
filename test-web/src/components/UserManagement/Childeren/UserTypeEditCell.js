import React from 'react';
import { Select, MenuItem } from '@mui/material';
import handleUserEdit from './handleUserEdit';

const UserTypeEditCell = ({
  id,
  field,
  value,
  api,
  setAllUsers,
  handleSnackbarShow,
}) => {
  const handleChange = async (event) => {
    const newValue = event.target.value;
    const success = await handleUserEdit(
      { id, field, value: newValue },
      handleSnackbarShow
    );
    if (success) {
      setAllUsers((prevUsers) =>
        prevUsers.map((user) =>
          user.id === id ? { ...user, [field]: newValue } : user
        )
      );
      api.setEditCellValue({ id, field, value: newValue }, event);
    }
  };
  return (
    <Select value={value} onChange={handleChange} sx={{ width: '140px' }}>
      <MenuItem value="Normal">Normal</MenuItem>
      <MenuItem value="Researcher">Researcher</MenuItem>
      <MenuItem value="Manager">Manager</MenuItem>
    </Select>
  );
};

export default UserTypeEditCell;
