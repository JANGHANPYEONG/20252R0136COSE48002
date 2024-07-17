import { Helmet } from 'react-helmet';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import LogIn from './routes/LogIn';
import Home from './routes/Home';
import Dashboard from './routes/Dashboard';
import Stats from './routes/Stats';
import PA from './routes/PA';
import Profile from './routes/Profile';
import DataEdit from './routes/DataEdit';
import UserManagement from './routes/UserManagement';
import DataConfirm from './routes/DataConfirm';
import DataPredict from './routes/DataPredict';
import Box from '@mui/material/Box';
import Sidebar from './components/Base/Sidebar';
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
      path: '/DataManage',
      title: 'DataManage | DeePlant',
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
      title: 'PA-one | DeePlant',
      component: <DataPredict />,
    },
    {
      path: '/PA',
      title: 'PA | DeePlant',
      component: <PA />,
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
  ];

  return (
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
                      <Sidebar />
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
  );
}

export default App;
