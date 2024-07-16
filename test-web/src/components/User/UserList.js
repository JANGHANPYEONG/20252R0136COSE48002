import * as React from 'react';
import Modal from 'react-bootstrap/Modal';
import UserRegister from './UserRegister';
import { useState, useEffect } from 'react';
import Typography from '@mui/material/Typography';
import { format } from 'date-fns';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import CustomSnackbar from '../Base/CustomSnackbar';
import DeleteIcon from '@mui/icons-material/Delete';
import InputBase from '@mui/material/InputBase';
import Toolbar from '@mui/material/Toolbar';
import { DataGrid } from '@mui/x-data-grid';
import IconButton from '@mui/material/IconButton';
import CircularProgress from '@mui/material/CircularProgress';
import SearchIcon from '@mui/icons-material/Search';
import { IoMdPersonAdd } from 'react-icons/io';
import { getAuth } from 'firebase/auth';
import { Box } from '@mui/material';
import { Button, Tooltip, OverlayTrigger } from 'react-bootstrap';
import { apiIP } from '../../config';

function UserList() {
  const [registerShow, setRegisterShow] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [editShow, setEditShow] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [usersData, setUsersData] = useState({});
  const [searchedUsers, setSearchedUsers] = useState([]);
  const handleRegisterClose = () => {
    setRegisterShow(false);
    window.location.reload();
  };
  const handleRegisterShow = () => setRegisterShow(true);
  const UserInfo = JSON.parse(localStorage.getItem('UserInfo'));

  const handleUserDelete = async (userId) => {
    try {
      const auth = getAuth();
      console.log(UserInfo.userId);
      console.log(userId);
      if (!UserInfo.userId) {
        showSnackbar('로그인이 필요합니다.', 'error');
        return;
      }

      if (UserInfo.userId === userId) {
        showSnackbar(
          '자신의 계정은 삭제할 수 없습니다. 회원탈퇴는 프로필 페이지에서 가능합니다.',
          'error'
        );
        return;
      }

      // If reauthentication is successful, proceed with the account deletion
      const response = await fetch(
        `http://${apiIP}/user/delete?userId=${userId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        // 삭제된 유저를 제외한 새로운 사용자 목록 업데이트
        setAllUsers((prevUsers) =>
          prevUsers.filter((user) => user.userId !== userId)
        );
        showSnackbar('사용자가 삭제되었습니다.', 'success');
        //delete user in firebase
      } else {
        showSnackbar('사용자 삭제에 실패했습니다.', 'error');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      showSnackbar('사용자 삭제 중 오류가 발생했습니다.', 'error');
    }
  };
  ///////////
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const showSnackbar = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const closeSnackbar = () => {
    setSnackbarOpen(false);
  };

  const renderTooltip = (props) => (
    <Tooltip id="button-tooltip" {...props}>
      신규 회원 등록
    </Tooltip>
  );
  ////////////

  const columns = [
    { field: 'name', headerName: '이름', width: 100 },
    { field: 'userId', headerName: '아이디', width: 250 },
    {
      field: 'type',
      headerName: '권한',
      width: 200,
      renderCell: (params) => (
        <CustomEditCell
          id={params.id}
          field={params.field}
          value={params.value}
          api={params.api}
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
          <IconButton onClick={() => handleUserDelete(params.row.userId)}>
            <DeleteIcon />
          </IconButton>
        </div>
      ),
    },
  ];
  useEffect(() => {
    const fetchData = async () => {
      try {
        //유저 리스트 fetch
        const usersListResponse = await fetch(`http://${apiIP}/user`);
        const usersData = await usersListResponse.json();

        const transformType = (type) => {
          switch (type) {
            case 0:
              return 'Normal';
            case 1:
              return 'Researcher';
            case 2:
              return 'Manager';
            default:
              return type;
          }
        };

        const usersWithTransformedType = usersData.map((user) => ({
          ...user,
          type: transformType(user.type),
        }));

        setUsersData(usersWithTransformedType);

        const usersWithAdditionalData = usersWithTransformedType.map(
          (user) => ({
            ...user,
            id: user.userId,
          })
        );

        setAllUsers(usersWithAdditionalData);

        setIsLoading(false); // Set isLoading to false after fetching data
      } catch (error) {
        console.log('Error fetching data:', error);
        setIsLoading(false); // Set isLoading to false in case of an error as well
      }
    };

    fetchData();
  }, []);

  const handleSearch = (event) => {
    const keyword = event.target.value.toLowerCase();
    if (!allUsers || allUsers.length === 0) {
      return; // Return early if allUsers is empty or not yet initialized
    }
    if (keyword === '') {
      setSearchedUsers([]); // Show no users if the search field is empty
    } else {
      const results = allUsers.filter(
        (user) =>
          user.name.toLowerCase().includes(keyword) ||
          user.userId.toLowerCase().includes(keyword) ||
          user.type.toLowerCase().includes(keyword) ||
          user.company.toLowerCase().includes(keyword) ||
          user.createdAt.toLowerCase().includes(keyword)
      );
      setSearchedUsers(results);
    }
  };

  const handleCellEdit = async (params) => {
    //유저 Type 수정
    const { id, field, value } = params;
    const userToUpdate = allUsers.find((user) => user.id === id);
    if (!userToUpdate || userToUpdate[field] === value) {
      return; // Return early if the value is not changed or the user is not found
    }

    try {
      // Send a POST request to update the user's information
      const response = await fetch(`http://${apiIP}/user/update`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: userToUpdate.userId,
          createdAt: userToUpdate.createdAt,
          updatedAt: userToUpdate.updatedAt, // Set the current date as updatedAt
          loginAt: userToUpdate.loginAt,
          password: userToUpdate.password,
          name: userToUpdate.name,
          company: userToUpdate.company,
          jobTitle: userToUpdate.jobTitle,
          homeAddr: userToUpdate.homeAddr,
          alarm: userToUpdate.alarm,
          type: value, // The new value for the "type" field
        }),
      });
      if (response.ok) {
        // If the update was successful, update the user's information in the state
        setAllUsers((prevUsers) =>
          prevUsers.map((user) =>
            user.id === id ? { ...user, [field]: value } : user
          )
        );
        showSnackbar(
          `${userToUpdate.name}님의 권한이 ${value}로 수정되었습니다. `,
          'success'
        );
      } else {
        console.log('Failed to update the user information');
      }
    } catch (error) {
      console.log('Error updating user information:', error);
    }
  };

  const CustomEditCell = ({ id, field, value, api }) => {
    const handleChange = (event) => {
      api.setEditCellValue({ id, field, value: event.target.value });
      handleCellEdit({ id, field, value: event.target.value });
    };

    return (
      <Select value={value} onChange={handleChange} sx={{ width: '140px' }}>
        <MenuItem value="Normal">Normal</MenuItem>
        <MenuItem value="Researcher">Researcher</MenuItem>
        <MenuItem value="Manager">Manager</MenuItem>
      </Select>
    );
  };

  return (
    <div>
      <Toolbar />
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Typography
          component="h2"
          variant="h4"
          gutterBottom
          style={{
            color: '#151D48',
            fontFamily: 'Poppins',
            fontSize: `${(36 / 1920) * 100}vw`,
            fontStyle: 'normal',
            fontWeight: 600,
            lineHeight: `${(36 / 1920) * 100 * 1.4}vw`,
          }}
        >
          User Management
        </Typography>
      </div>
      <Modal
        show={registerShow}
        onHide={handleRegisterClose}
        backdrop="true"
        keyboard={false}
        centered
      >
        <Modal.Body>
          <Modal.Title
            style={{
              color: '#151D48',
              fontFamily: 'Poppins',
              fontSize: `${(36 / 1920) * 100}vw`,
              fontWeight: 600,
              lineHeight: `${(36 / 1920) * 100 * 1.4}vw`,
            }}
          >
            신규 회원 등록
          </Modal.Title>
          <UserRegister handleClose={handleRegisterClose} />
        </Modal.Body>
      </Modal>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Box
          component="form"
          sx={{
            marginBottom: `${(16 / 1080) * 100}vh`,
            paddingX: `${(16 / 1920) * 100}vw`,
            paddingY: `${(12 / 1080) * 100}vh`,
            width: `${(513 / 1920) * 100}vw`,
            height: `${(60 / 1080) * 100}vh`,
            backgroundColor: '#FFF',
          }}
        >
          <SearchIcon />
          <InputBase
            placeholder=" 사용자 검색"
            onChange={(event) => handleSearch(event)}
            sx={{
              color: '#737791',
              fontFamily: 'Poppins',
              fontSize: `${(20 / 1920) * 100}vw`,
              fontStyle: 'normal',
              fontWeight: 500,
              lineHeight: `${(20 / 1080) * 100}vh`,
            }}
          />
        </Box>

        <div style={{ marginLeft: 'auto' }}>
          <OverlayTrigger
            placement="top"
            delay={{ show: 250, hide: 400 }}
            overlay={renderTooltip}
          >
            <Button
              className="mb-3"
              onClick={handleRegisterShow}
              style={{
                display: 'inline-flex',
                paddingX: `${(12 / 1920) * 100}vw`,
                paddingY: `${(16 / 1080) * 100}vh`,
                alignItems: 'center',
                gap: `${(8 / 1920) * 100}vw`,
                borderRadius: `${(10 / 1920) * 100}vw`,
                background: '#32CD32',
                borderColor: '#32CD32',
              }}
            >
              <IoMdPersonAdd />
            </Button>
          </OverlayTrigger>
        </div>
      </div>

      {isLoading ? (
        <CircularProgress />
      ) : (
        <DataGrid
          rows={searchedUsers.length > 0 ? searchedUsers : allUsers}
          columns={columns.map((column) =>
            column.field === 'type'
              ? { ...column, editable: true } // Enable editing for the "type" field
              : column
          )}
          pageSize={5}
          pageSizeOptions={[5, 10, 20]}
          pagination
          autoHeight
          onEditCellChange={handleCellEdit} // Attach the event handler for cell edits
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: 5,
              },
            },
          }}
          //pageSizeOptions={[5]}
          disableRowSelectionOnClick
          sx={{
            width: `${(1470 / 1920) * 100}vw`,
            height: `${(560 / 1080) * 100}vh`,
            flexShrink: 0,
            borderRadius: `${(20 / 1920) * 100}vw`,
            border: '1px solid #F8F9FA',
            backgroundColor: '#FFF',
            boxShadow: `${(0 / 1920) * 100}vw ${(4 / 1080) * 100}vh ${
              (20 / 1920) * 100
            }vw ${(0 / 1080) * 100}vh rgba(238, 238, 238, 0.50)`,
          }}
        />
      )}
      <CustomSnackbar
        open={snackbarOpen}
        message={snackbarMessage}
        severity={snackbarSeverity}
        onClose={closeSnackbar}
      />
    </div>
  );
}

export default UserList;
