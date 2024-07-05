import * as React from 'react';
import { useEffect, useState } from 'react';
import { BarChart } from '@mui/x-charts/BarChart';
import { apiIP } from '../../../config';

export default function BarGraph() {
  const [chartData, setChartData] = useState([]); // Initialize with an empty array

  useEffect(() => {
    // Fetch data from the API
    fetch(`http://${apiIP}/meat/statistic?type=0`)
      .then((response) => response.json())
      .then((data) => {
        // Extract relevant data from the API response and transform it to match BarChart data structure
        const cattleProcessed = data.cattle_counts.processed;
        const cattleRaw = data.cattle_counts.raw;
        const pigProcessed = data.pig_counts.processed;
        const pigRaw = data.pig_counts.raw;

        // Set the transformed data to the state
        setChartData([
          { group: 'Cattle Processed', value: cattleProcessed },
          { group: 'Cattle Raw', value: cattleRaw },
          { group: 'Pig Processed', value: pigProcessed },
          { group: 'Pig Raw', value: pigRaw },
        ]);
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  }, []);

  // Wait for the API call to complete and the state to be updated
  if (chartData.length === 0) {
    return null;
  }

  return (
    <BarChart
      xAxis={[{ scaleType: 'band', data: chartData.map((item) => item.group) }]}
      series={[{ data: chartData.map((item) => item.value) }]}
      width={500}
      height={300}
    />
  );
}
