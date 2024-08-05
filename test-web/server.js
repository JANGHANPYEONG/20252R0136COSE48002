const http = require('http');
const express = require('express');
const path = require('path');
const axios = require('axios');
const dotenv = require('dotenv')

dotenv.config();

const app = express();
const port = process.env.REACT_APP_PORT;

const server = process.env.REACT_APP_SERVER_API;
const serverPort = process.env.REACT_APP_SERVER_PORT;

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'build')));

// API endpoint to ping the server
app.get('/ping', (req, res) => {
  res.send('pong');
});

// Route to proxy API requests to Flask backend
app.get('/api/*', (req, res) => {
  const apiEndpoint = req.url.replace(/^\/api/, ''); // Remove '/api' prefix
  const apiUrl = `http://${server}:${serverPort}${apiEndpoint}`; // Adjust as per your Flask backend URL

  axios
    .get(apiUrl)
    .then((response) => {
      res.json(response.data);
    })
    .catch((error) => {
      console.error('Error proxying API request:', error);
      res.status(500).send('Error fetching data');
    });
});

// Route all other requests to React's index.html
app.get('/*', (req, res) => {
  res.set({
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    Pragma: 'no-cache',
    Date: Date.now(),
  });
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// Start the server
http.createServer(app).listen(port, () => {
  console.log(`App listening at http://${server}:${port}`);
});
