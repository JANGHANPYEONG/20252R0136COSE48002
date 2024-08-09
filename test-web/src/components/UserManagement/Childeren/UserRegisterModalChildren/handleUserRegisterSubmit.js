/** 유저 등록 함수 */
import {
  getAuth,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
} from 'firebase/auth';
import { userRegister } from '../../../../API/user/userRegister';

const handleUserRegisterSubmit = async (submitData) => {
  const {
    event,
    setValidated,
    isFormValid,
    setIsLoading,
    setCreatedAt,
    userId,
    name,
    company,
    jobTitle,
    homeAddr,
    alarm,
    type,
    setShowCompletionModal,
  } = submitData;
  const auth = getAuth();

  const generateTempPassword = () => {
    const characters =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const length = 10;
    let tempPassword = '';
    for (let i = 0; i < length; i++) {
      tempPassword += characters.charAt(
        Math.floor(Math.random() * characters.length)
      );
    }
    return tempPassword;
  };

  if (event && event.preventDefault) {
    event.preventDefault();
  }

  const form = event ? event.currentTarget : null;
  if (form && form.checkValidity() === false) {
    event.stopPropagation();
    setValidated(true);
    return;
  }

  if (isFormValid()) {
    setIsLoading(true);
    try {
      setCreatedAt(new Date().toISOString().slice(0, -5));
      const req = {
        userId: userId,
        name: name,
        company: company,
        jobTitle: jobTitle,
        homeAddr: homeAddr,
        alarm: alarm,
        type: type,
      };

      const registrationResponse = await userRegister(req);
      if (registrationResponse.ok) {
        const tempPassword = generateTempPassword();
        const { user } = await createUserWithEmailAndPassword(
          auth,
          userId,
          tempPassword
        );
        await sendPasswordResetEmail(auth, userId);

        console.log('User registered successfully');
        setShowCompletionModal(true);
      } else {
        console.error('User registration failed');
        // Add additional error handling or notifications as needed
      }
    } catch (error) {
      console.error('Error during registration:', error);
      // Add additional error handling or notifications as needed
    } finally {
      setIsLoading(false);
    }
  }
  setValidated(true);
};

export default handleUserRegisterSubmit;
