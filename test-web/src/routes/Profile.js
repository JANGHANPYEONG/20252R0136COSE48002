import React, { useState } from "react";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Modal from "@mui/material/Modal";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { CircularProgress } from "@mui/material";
import { getAuth } from "firebase/auth";
import { useNavigate } from "react-router-dom";
import CustomSnackbar from "../components/Base/CustomSnackbar";
import { apiIP } from "../config";

const UserInfo = JSON.parse(localStorage.getItem("UserInfo"));

export default function Profile() {
  const [updatedUserInfo, setUpdatedUserInfo] = useState(UserInfo);
  const [isUpdating, setIsUpdating] = useState(false);

  const [name, setName] = useState(UserInfo.name);
  const [company, setCompany] = useState(UserInfo.company);
  const [jobTitle, setJobTitle] = useState(UserInfo.jobTitle);
  const [homeAddr, setHomeAddr] = useState(UserInfo.homeAddr);
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const deleteself = async () => {
    try {
      const auth = getAuth();
      const user = auth.currentUser;

      const response = await fetch(
        `http://${apiIP}/user/delete?id=${user.email}`
      );

      if (response.ok) {
        localStorage.setItem("isLoggedIn", "false");
        navigate("/");
        window.location.reload();
      }
    } catch (error) {
      console.error("Error deleting user:", error);
    }
  };

  // Function to handle user information update
  const updateUserInfo = async () => {
    setIsUpdating(true);
    try {
      const response = await fetch(`http://${apiIP}/user/update`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          // local storage에 저장되어 있지 않은 정보들은 주석 처리
          userId: UserInfo.userId,
          // password: UserInfo.password,
          name: name,
          company: company,
          jobTitle: jobTitle,
          homeAddr: homeAddr,
          // alarm: UserInfo.alarm,
          // type: UserInfo.type,
          // updatedAt: UserInfo.updatedAt,
          // loginAt: UserInfo.loginAt,
          // createdAt: UserInfo.createdAt,
        }),
      });
      if (response.ok) {
        const updatedData = JSON.stringify({
          userId: UserInfo.userId,
          // password: UserInfo.password,
          name: name,
          company: company,
          jobTitle: jobTitle,
          homeAddr: homeAddr,
          // alarm: UserInfo.alarm,
          type: UserInfo.type,
          // updatedAt: UserInfo.updatedAt,
          // loginAt: UserInfo.loginAt,
          // createdAt: UserInfo.createdAt,
        });
        setUpdatedUserInfo(updatedData);
        localStorage.setItem("UserInfo", updatedData);
        window.location.reload();
        showSnackbar("회원정보가 수정되었습니다.", "success");
      } else {
        showSnackbar("회원정보 수정에 실패했습니다.", "error");
      }
    } catch (error) {
      console.log("Error updating user information:", error);
      showSnackbar("서버와 통신 중 오류가 발생했습니다.", "error");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === "name") {
      setName(value);
    } else if (name === "company") {
      setCompany(value);
    } else if (name === "jobTitle") {
      setJobTitle(value);
    } else if (name === "homeAddr") {
      setHomeAddr(value);
    }
  };

  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  const showSnackbar = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const closeSnackbar = () => {
    setSnackbarOpen(false);
  };

  return (
    <Paper sx={{ p: 2 }}>
      <div style={{ marginBottom: "1rem" }}>
        <TextField
          label="회원가입일"
          name="createdAt"
          value={updatedUserInfo.createdAt}
          disabled
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <TextField
          label="업데이트일"
          name="updatedAt"
          value={updatedUserInfo.updatedAt}
          disabled
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <TextField
          label="권한"
          name="type"
          value={updatedUserInfo.type}
          disabled
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <TextField
          label="이름"
          name="name"
          value={name}
          onChange={handleInputChange}
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <TextField
          label="직장"
          name="company"
          value={company}
          onChange={handleInputChange}
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <TextField
          label="직책"
          name="jobTitle"
          value={jobTitle}
          onChange={handleInputChange}
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <TextField
          label="주소"
          name="homeAddr"
          value={homeAddr}
          onChange={handleInputChange}
        />
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <Button
          style={{ margin: "0.5rem" }}
          variant="contained"
          onClick={updateUserInfo}
          disabled={isUpdating}
        >
          {isUpdating ? <CircularProgress size={24} /> : "정보 수정"}
        </Button>
        <Button
          variant="contained"
          onClick={handleOpenModal}
          style={{ backgroundColor: "red", color: "white", margin: "0.5rem" }}
        >
          회원 탈퇴
        </Button>
      </div>

      <Modal
        open={isModalOpen}
        onClose={handleCloseModal}
        aria-labelledby="confirm-delete-modal"
        aria-describedby="confirm-delete-description"
      >
        <Box
          sx={{
            position: "absolute",
            width: 300,
            backgroundColor: "white",
            borderRadius: 8, // 더 둥글게
            boxShadow: 5, // 그림자 추가
            p: 2,
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            textAlign: "center",
          }}
        >
          <Typography variant="h6" id="modal-modal-title" component="div">
            회원 탈퇴 확인
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            정말로 회원 탈퇴하시겠습니까? <br />이 작업은 취소할 수 없습니다.
          </Typography>
          <Button variant="contained" onClick={deleteself}>
            확인
          </Button>
          <Button
            variant="contained"
            onClick={handleCloseModal}
            style={{ marginLeft: "1rem" }}
          >
            취소
          </Button>
        </Box>
      </Modal>

      <CustomSnackbar
        open={snackbarOpen}
        message={snackbarMessage}
        severity={snackbarSeverity}
        onClose={closeSnackbar}
      />
    </Paper>
  );
}
