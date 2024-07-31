import { useNavigate } from "react-router-dom";

const useLogout = () => {
    const navigate = useNavigate();

    const logout = async () => {
        try {
            localStorage.setItem('isLoggedIn', 'false');
            navigate('/');
            window.location.reload();
        } catch (error) {
            console.log(error.message);
        }
    };

    return logout;
};

export default useLogout;
