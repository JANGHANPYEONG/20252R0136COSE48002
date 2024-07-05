import ApexCharts from "react-apexcharts";
import React, { useEffect, useState } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import { apiIP } from "../../../../config";

export default function Sens_ProcMeat({ startDate, endDate }) {
  const [chartData, setChartData] = useState([]);

  const fetchData = async () => {
    try {
      const response = await fetch(
        `http://${apiIP}/meat/statistic/sensory-stats/processed?start=${startDate}&end=${endDate}`
      );

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setChartData(data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [startDate, endDate]);

  const calculateBoxPlotStatistics = (data) => {
    const sortedData = data.sort((a, b) => a - b);
    const q1Index = Math.floor(sortedData.length / 4);
    const medianIndex = Math.floor(sortedData.length / 2);
    const q3Index = Math.floor((3 * sortedData.length) / 4);

    const q1 = sortedData[q1Index];
    const median = sortedData[medianIndex];
    const q3 = sortedData[q3Index];
    const min = sortedData[0];
    const max = sortedData[sortedData.length - 1];
    return [min, q1, median, q3, max];
  };

  const chartOptions = {
    chart: {
      type: "boxPlot",
      height: 350,
    },
  };

  // Conditionally render the chart only when chartData is not empty
  return (
    <div>
      {chartData && chartData.color && chartData.color.unique_values ? (
        <ApexCharts
          series={[
            {
              type: "boxPlot",
              data: [
                {
                  x: "Color",
                  y: calculateBoxPlotStatistics(chartData.color.unique_values),
                },
                {
                  x: "Marbling",
                  y: calculateBoxPlotStatistics(
                    chartData.marbling.unique_values
                  ),
                },
                {
                  x: "Overall",
                  y: calculateBoxPlotStatistics(
                    chartData.overall.unique_values
                  ),
                },
                {
                  x: "SurfaceMoisture",
                  y: calculateBoxPlotStatistics(
                    chartData.surfaceMoisture.unique_values
                  ),
                },
                {
                  x: "Texture",
                  y: calculateBoxPlotStatistics(
                    chartData.texture.unique_values
                  ),
                },
              ],
            },
          ]}
          options={chartOptions}
          type="boxPlot"
          height={350}
        />
      ) : (
        <CircularProgress />
      )}
    </div>
  );
}
