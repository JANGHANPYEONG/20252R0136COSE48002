/** 매니저의 유저 삭제 함수. (탈퇴는 Profile의 deleteSelf) */
// import { getAuth } from 'firebase/auth';
import { userDelete } from '../../../API/user/userDelete';

const handleUserDelete = async (userId, UserInfo, handleSnackbarShow) => {
  try {
    // const auth = getAuth();
    if (!UserInfo.userId) {
      handleSnackbarShow('로그인이 필요합니다.', 'error');
      return;
    }

    if (UserInfo.userId === userId) {
      handleSnackbarShow(
        '자신의 계정은 삭제할 수 없습니다. 회원탈퇴는 프로필 페이지에서 가능합니다.',
        'error'
      );
      return;
    }

    // If reauthentication is successful, proceed with the account deletion
    // delete user in firebase
    const response = await userDelete(userId);
    if (response.ok) {
      handleSnackbarShow('사용자가 삭제되었습니다.', 'success');
      return true;
    } else {
      handleSnackbarShow('사용자 삭제에 실패했습니다.', 'error');
      return false;
    }
  } catch (error) {
    console.error('Error deleting user:', error);
    handleSnackbarShow('사용자 삭제 중 오류가 발생했습니다.', 'error');
    return false;
  }
};

export default handleUserDelete;
