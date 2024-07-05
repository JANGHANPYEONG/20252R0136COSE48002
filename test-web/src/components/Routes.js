import React from 'react';
import { Route, Navigate } from 'react-router-dom';
import isLogin from '../Utils/isLogin';

// PublicRoute 컴포넌트는 로그인한 사용자에게 접근을 허용하지 않음
const PublicRoute = ({ component: Component, restricted, ...rest }) => {
  return (
    <Route
      {...rest}
      render={(props) =>
        isLogin() && restricted ? (
          <Navigate to="/login" />
        ) : (
          <Component {...props} />
        )
      }
    />
  );
};

// PrivateRoute 컴포넌트는 로그인하지 않은 사용자에게 접근을 허용하지 않음
const PrivateRoute = ({ component: Component, ...rest }) => {
  return (
    console.log(isLogin()),
    (
      <Route
        {...rest}
        render={(props) =>
          isLogin() ? <Component {...props} /> : <Navigate to="/home" />
        }
      />
    )
  );
};

export { PublicRoute, PrivateRoute };
