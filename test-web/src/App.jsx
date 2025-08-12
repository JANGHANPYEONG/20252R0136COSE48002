import { Helmet } from 'react-helmet';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import LogIn from './routes/LogIn';
import Home from './routes/Home';
import Normal from './routes/Normal';
import Dashboard from './routes/Dashboard';
import Stats from './routes/Stats';
import Profile from './routes/Profile';
import DataEdit from './routes/DataEdit';
import UserManagement from './routes/UserManagement';
import DataConfirm from './routes/DataConfirm';
import DataPredict from './routes/DataPredict';
import SpectroPattern from './routes/spectro_pattern';
import Learning from './routes/Learning';
import Predict from './routes/Predict';
import LearningRGB from './routes/LearningRGB';
import PredictRGB from './routes/PredictRGB';
import Data from './routes/Data';
import DataRegister from './routes/DataRegister';
import NewDashboard from './routes/NewDashboard';
import MeatDetailPage from './routes/MeatDetailPage'; // 목업 페이지 임포트
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
      path: '/Pattern',
      title: 'Pattern | DeePlant',
      component: <SpectroPattern />,
    },
    {
      path: '/Learning',
      title: 'Learning | DeePlant',
      component: <Learning />,
    },
    {
      path: '/Learning/RGB',
      title: 'LearningRGB | DeePlant',
      component: <LearningRGB />,
    },
    {
      path: '/Predict',
      title: 'Predict | DeePlant',
      component: <Predict />,
    },
    {
      path: '/Predict/RGB',
      title: 'PredictRGB | DeePlant',
      component: <PredictRGB />,
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
      path: '/NewDashboard',
      title: 'NewDashboard | Deeplant',
      component: <NewDashboard />,
    },
    {
      path: '/meat/:id',
      title: 'Meat Detail | Deeplant',
      component: <MeatDetailPage />,
    }, // 목업 페이지 라우팅
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
