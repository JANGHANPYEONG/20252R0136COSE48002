import LogInField from '../components/LogIn/LogInField';
// import { UserProvider } from '../Utils/UserContext';

const LogIn = () => {
  return (
    // Wrap the LogIn component with the UserProvider
    // <UserProvider>
    <div className="d-flex  align-items-center" style={{ height: '100vh' }}>
      <LogInField />
    </div>
    // </UserProvider>
  );
};

export default LogIn;
