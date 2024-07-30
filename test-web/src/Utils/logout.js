import { useNavigate } from "react-router-dom";

const logout = async () => {
    const navigate = useNavigate();
    try {
      localStorage.setItem('isLoggedIn', 'false');
      navigate('/');
      window.location.reload();
    } catch (error) {
      console.log(error.message);
    }
  };
export default logout