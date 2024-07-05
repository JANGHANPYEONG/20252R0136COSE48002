import * as React from 'react';
import { useEffect, useState } from 'react';
import { PieChart } from '@mui/x-charts/PieChart';
import { apiIP } from '../../../config';

export default function BasicPie() {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    // Fetch data from the API
    fetch(`http://${apiIP}/meat/statistic?type=0`)
      .then((response) => response.json())
      .then((data) => {
        // Extract relevant data from the API response and transform it to match PieChart data structure
        const cattleProcessed = data.cattle_counts.processed;
        const cattleRaw = data.cattle_counts.raw;
        const pigProcessed = data.pig_counts.processed;
        const pigRaw = data.pig_counts.raw;

        const chartData = [
          { id: 0, value: cattleProcessed, label: 'Cattle Processed' },
          { id: 1, value: cattleRaw, label: 'Cattle Raw' },
          { id: 2, value: pigProcessed, label: 'Pig Processed' },
          { id: 3, value: pigRaw, label: 'Pig Raw' },
        ];

        // Set the transformed data to the state
        setChartData(chartData);
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  }, []);

  // Wait for the API call to complete and the state to be updated
  if (chartData.length === 0) {
    return null;
  }

  return <PieChart series={[{ data: chartData }]} width={600} height={200} />;
}
