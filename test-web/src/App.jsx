import { Helmet } from 'react-helmet';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import LogIn from './routes/LogIn';
import Home from './routes/Home';
import Normal from './routes/Normal';
import Dashboard from './routes/Dashboard';
import Stats from './routes/Stats';
import PA from './routes/PA';
import Profile from './routes/Profile';
import DataEdit from './routes/DataEdit';
import UserManagement from './routes/UserManagement';
import DataConfirm from './routes/DataConfirm';
import DataPredict from './routes/DataPredict';
import Spectro from './routes/spectro';
import SpectroPattern from './routes/spectro_pattern';
import SpectroTrain from './routes/spectro_train';
import SpectroPredict from './routes/spectro_predict';
import Data from './routes/Data';
import AI from './routes/AI';
import DataRegister from './routes/DataRegister';

import { UserProvider } from './Utils/UserContext';

import Box from '@mui/material/Box';
import MainWidgetBars from './components/Base/WidgetBars/MainWidgetBars';
import { createTheme, ThemeProvider } from '@mui/material/styles';
const defaultTheme = createTheme();

function App() {
  const isLoggedin = localStorage.getItem('isLoggedIn') === 'true';
  console.log(isLoggedin);

  const routes = [
    {
      path: '/',
      title: 'LogIn | DeePlant',
      component: isLoggedin ? <Home /> : <LogIn />,
    },
    {
      path: '/Home',
      title: 'Home | DeePlant',
      component: <Home />,
    },
    {
      path: '/normal',
      title: 'Normal | DeePlant',
      component: <Normal />,
    },
    {
      path: '/spectro',
      title: 'Spectro | DeePlant',
      component: <Spectro />,
    },
    {
      path: '/spectro/pattern',
      title: 'Spectro Pattern | DeePlant',
      component: <SpectroPattern />,
    },
    {
      path: '/spectro/train',
      title: 'Spectro Train | DeePlant',
      component: <SpectroTrain />,
    },
    {
      path: '/spectro/predict',
      title: 'Spectro Predict | DeePlant',
      component: <SpectroPredict />,
    },
    {
      path: '/Data',
      title: 'Data | DeePlant',
      component: <Data />,
    },
    {
      path: '/DataManage',
      title: 'DataManage | DeePlant',
      component: <Dashboard />,
    },
    {
      path: '/DataRegister',
      title: 'DataRegister | DeePlant',
      component: <DataRegister />,
    },
    {
      path: '/DashBoard',
      title: 'DashBoard | DeePlant',
      component: <Dashboard />,
    },
    {
      path: '/DataConfirm/:id',
      title: 'DataConfirm | Deeplant',
      component: <DataConfirm />,
    },
    {
      path: '/dataView/:id',
      title: 'DataView | DeePlant',
      component: <DataEdit />,
    },
    {
      path: '/dataPA/:id',
      title: 'DataPredict | DeePlant',
      component: <DataPredict />,
    },
    {
      path: '/PA',
      title: 'PA | DeePlant',
      component: <PA />,
    },
    {
      path: '/Pattern',
      title: 'Pattern | DeePlant',
      component: <SpectroPattern />,
    },
    {
      path: '/Learning',
      title: 'Learning | DeePlant',
      component: <SpectroTrain />,
    },
    {
      path: '/Predict',
      title: 'Predict | DeePlant',
      component: <SpectroPredict />,
    },
    {
      path: '/Stats',
      title: 'Statistics | DeePlant',
      component: <Stats />,
    },
    {
      path: '/stats',
      title: 'Statistics | DeePlant',
      component: <Stats />,
    },
    {
      path: '/profile',
      title: 'Profile | DeePlant',
      component: <Profile />,
    },
    {
      path: '/UserManagement',
      title: 'UserManage | Deeplant',
      component: <UserManagement />,
    },
    {
      path: '/AI',
      title: 'AI | DeePlant',
      component: <AI />,
    },
  ];

  return (
    <UserProvider>
      <Router>
        <Routes>
          {routes.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={
                <>
                  <Helmet>
                    <title>{route.title}</title>
                  </Helmet>
                  <ThemeProvider theme={defaultTheme}>
                    {!isLoggedin ? (
                      <LogIn />
                    ) : (
                      <Box sx={{ display: 'flex' }}>
                        {route.path !== '/' && <MainWidgetBars />}
                        <Box
                          component="main"
                          sx={{
                            backgroundColor: '#FAFBFC',
                            flexGrow: 1,
                            height: '100vh',
                            overflow: 'auto',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexDirection: 'column',
                          }}
                        >
                          {route.component}
                        </Box>
                      </Box>
                    )}
                  </ThemeProvider>
                </>
              }
            />
          ))}
        </Routes>
      </Router>
    </UserProvider>
  );
}

export default App;
