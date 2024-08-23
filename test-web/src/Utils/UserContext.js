// UserContext.js

import { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

const UserProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('UserInfo');
    return savedUser ? JSON.parse(savedUser) : {};
  });

  useEffect(() => {
    localStorage.setItem('UserInfo', JSON.stringify(user));
  }, [user]);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};

const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context.user;
};

const useSetUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useSetUser must be used within a UserProvider');
  }
  return context.setUser;
};

export { UserProvider, useUser, useSetUser };
