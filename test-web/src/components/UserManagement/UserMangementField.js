/*가입된 유저 정보를 표시 및 검색*/
/*유저 등록, 삭제, 수정 기능 총괄. 관련 컴포넌트, handle 함수와 연결*/
import { React, useState, useEffect } from 'react';
import {
  Typography,
  InputBase,
  Toolbar,
  Box,
  CircularProgress,
} from '@mui/material';
import { Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { DataGrid } from '@mui/x-data-grid';
import SearchIcon from '@mui/icons-material/Search';
import { IoMdPersonAdd } from 'react-icons/io';

import CustomSnackbar from '../Base/CustomSnackbar';

import DeleteConfirmationModal from './Childeren/DeleteConfirmationModal';
import UserRegisterModal from './Childeren/UserRegisterModal';

import handleUserDelete from './Childeren/handleUserDelete';
import handleUserSearch from './Childeren/handleUserSearch';

import { userList } from '../../API/user/userList';
import UserTable from './Childeren/UserTable';

const UserList = () => {
  const [isLoading, setIsLoading] = useState(true);

  // const [editShow, setEditShow] = useState(false);
  // const [selectedUser, setSelectedUser] = useState(null);
  // const [users, setUsers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [usersData, setUsersData] = useState({});
  const [searchedUsers, setSearchedUsers] = useState([]);

  const [registerShow, setRegisterShow] = useState(false);
  const [deleteConfirmShow, setDeleteConfirmShow] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const UserInfo = JSON.parse(localStorage.getItem('UserInfo'));

  const handleRegisterShow = () => setRegisterShow(true);

  const handleRegisterClose = () => {
    setRegisterShow(false);
  };

  const handleDeleteConfirmShow = (user) => {
    setUserToDelete(user);
    setDeleteConfirmShow(true);
  };

  const handleDeleteConfirmClose = () => {
    setDeleteConfirmShow(false);
    setUserToDelete(null);
  };

  const handleDeleteConfirmed = async () => {
    if (userToDelete) {
      const success = await handleUserDelete(
        userToDelete?.userId,
        UserInfo,
        handleSnackbarShow
      );
      if (success) {
        // 삭제된 유저를 제외한 새로운 사용자 목록 업데이트
        setAllUsers((prevUsers) =>
          prevUsers.filter((user) => user.userId !== userToDelete?.userId)
        );
        handleDeleteConfirmClose();
      }
    }
  };

  const handleSnackbarShow = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        //유저 리스트 fetch
        const usersListResponse = await userList();
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

  return (
    <div
      style={{
        // alignContent: 'center',
        overflow: 'auto',
        width: '100%', //
        marginTop: '100px',
        paddingBottom: '100px',
        marginLeft: `${(720 / 1920) * 100}vw`, //
        // marginright: `${(380 / 1920) * 100}vw`, //
      }}
    >
      <Toolbar />
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Typography
          component="h2"
          variant="h4"
          gutterBottom
          style={{
            color: '#151D48',
            fontFamily: 'Poppins',
            fontSize: `30px`,
            fontStyle: 'normal',
            fontWeight: 600,
            // lineHeight: `${(36 / 1920) * 100 * 1.4}vw`,
          }}
        >
          User Management
        </Typography>
      </div>

      <UserRegisterModal show={registerShow} onHide={handleRegisterClose} />

      <DeleteConfirmationModal
        show={deleteConfirmShow}
        onHide={handleDeleteConfirmClose}
        onConfirm={handleDeleteConfirmed}
        userName={userToDelete?.name}
        userId={userToDelete?.userId}
      />

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          // maxWidth: `${(1470 / 1920) * 100}vw`,
          maxWidth: '1040px',
        }}
      >
        <Box
          component="form"
          sx={{
            marginBottom: `${(16 / 1080) * 100}vh`,
            paddingX: `8px`,
            paddingY: `8px`,
            width: '280px',
            height: '50px',
            // minHeight: '60px',
            backgroundColor: '#FFF',
          }}
        >
          <SearchIcon />
          <InputBase
            placeholder=" 사용자 검색"
            onChange={(event) =>
              handleUserSearch(event, allUsers, setSearchedUsers)
            }
            sx={{
              color: '#737791',
              fontFamily: 'Poppins',
              fontSize: `18px`,
              fontStyle: 'normal',
              fontWeight: 500,
              // lineHeight: `${(20 / 1080) * 100}vh`,
            }}
          />
        </Box>

        <div style={{ marginLeft: 'auto' }}>
          <OverlayTrigger
            placement="top"
            delay={{ show: 250, hide: 400 }}
            overlay={<Tooltip id="button-tooltip">신규 회원 등록</Tooltip>}
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
          columns={UserTable(
            handleDeleteConfirmShow,
            setAllUsers,
            handleSnackbarShow
          ).map((column) =>
            column.field === 'type'
              ? { ...column, editable: true } // Enable editing for the "type" field
              : column
          )}
          pageSize={5}
          pageSizeOptions={[5, 10, 20]}
          pagination
          autoHeight
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
            maxWidth: '1040px',
          }}
        />
      )}
      <CustomSnackbar
        open={snackbarOpen}
        message={snackbarMessage}
        severity={snackbarSeverity}
        onClose={handleSnackbarClose}
      />
    </div>
  );
};

export default UserList;
