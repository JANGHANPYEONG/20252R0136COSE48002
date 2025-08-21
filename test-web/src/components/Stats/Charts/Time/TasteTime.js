import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { statisticTime } from '../../../../API/statistic/statisticTime';

const TasteTime = ({ startDate, endDate, seqnoValue, meatValue, dataType, modality }) => {
  const [series, setSeries] = useState([
    {
      name: 'Deep Aging',
      data: [], // We will update this with the actual data points later
    },
    {
      name: 'Raw Meat',
      data: [], // We will update this with the actual data points later
    },
  ]);

  // 숙성도 비교 차트와 동일한 레이블 선택 필터
  const availableLabels = [
    { value: 'label1', name: '단백질 함량' },
    { value: 'label2', name: '지방 함량' },
    { value: 'label3', name: '수분 함량' },
    { value: 'label4', name: 'pH 값' },
    { value: 'label5', name: '색도 값' },
  ];
  const [selectedLabel, setSelectedLabel] = useState('label1');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await statisticTime(
          startDate,
          endDate,
          seqnoValue,
          meatValue
        );
        const freshmeat = await statisticTime(startDate, endDate, 1, meatValue); //시계열 api 호출
        const data = await response.json();
        const freshmeat_data = await freshmeat.json();

        // Extract the necessary data from the response
        const deepAgingData = [
          parseFloat(data[0].toFixed(2)), // 0일
          parseFloat(data[2].toFixed(2)), // 7일
        ];

        const rawMeatData = [
          parseFloat(freshmeat_data[1].toFixed(2)),
          parseFloat(freshmeat_data[1].toFixed(2)),
        ];

        // Pad to pull points inward from extremes
        const deepAgingPadded = [null, deepAgingData[0], deepAgingData[1], null];
        const rawMeatPadded = [null, rawMeatData[0], rawMeatData[1], null];

        // Update the chart data
        setSeries([
          {
            name: 'Deep Aging',
            data: deepAgingPadded,
          },
          {
            name: 'Raw Meat',
            data: rawMeatPadded,
          },
        ]);
      } catch (error) {
        console.error('Error fetching data:', error);
        // Dummy data fallback for future API integration (0일, 7일만)
        const deepAgingData = [
          Number((Math.random() * 2 + 4).toFixed(2)), // 0일
          Number((Math.random() * 2 + 6).toFixed(2)), // 7일
        ];
        const rawMeatBase = Number((Math.random() * 1.5 + 4).toFixed(2));
        const rawMeatData = [rawMeatBase, rawMeatBase];
        const deepAgingPadded = [null, deepAgingData[0], deepAgingData[1], null];
        const rawMeatPadded = [null, rawMeatData[0], rawMeatData[1], null];

        setSeries([
          {
            name: 'Deep Aging',
            data: deepAgingPadded,
          },
          {
            name: 'Raw Meat',
            data: rawMeatPadded,
          },
        ]);
      }
    };

    fetchData();
  }, [startDate, endDate, meatValue, seqnoValue, dataType, modality, selectedLabel]);

  const options = {
    chart: {
      height: 350,
      type: 'line',
      dropShadow: {
        enabled: true,
        color: '#000',
        top: 18,
        left: 7,
        blur: 10,
        opacity: 0.2,
      },
      toolbar: {
        show: false,
      },
    },
    colors: ['#77B6EA', '#545454'],
    dataLabels: {
      enabled: true,
    },
    stroke: {
      curve: 'smooth',
    },
    title: {
      text: `[${modality}] 숙성 시간에 따른 ${dataType === 'sensory' ? '관능' : '예측'} 데이터 변화 - ${availableLabels.find(l => l.value === selectedLabel)?.name}`,
      align: 'left',
    },
    grid: {
      borderColor: '#e7e7e7',
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5,
      },
    },
    markers: {
      size: 1,
    },
    xaxis: {
      categories: ['', '0일', '7일', ''],
      title: {
        text: '숙성일',
      },
    },
    yaxis: {
      title: {
        text: '연도 (Tenderness)',
      },
      min: 0,
      max: 10,
      labels: {
        formatter: (value) => parseFloat(value).toFixed(2), // Format the y-axis labels to 2 decimal places
      },
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
      floating: true,
      offsetY: -25,
      offsetX: -5,
    },
  };

  return (
    <Box>
      {/* 레이블 선택 드롭다운 (숙성도 비교 차트와 동일 구조) */}
      <Box mb={2}>
        <FormControl fullWidth size="small">
          <InputLabel id="ts-label-select-label">분석할 레이블 선택</InputLabel>
          <Select
            labelId="ts-label-select-label"
            id="ts-label-select"
            value={selectedLabel}
            label="분석할 레이블 선택"
            onChange={(e) => setSelectedLabel(e.target.value)}
            size="small"
            sx={{ '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
          >
            {availableLabels.map((label) => (
              <MenuItem key={label.value} value={label.value}>
                {label.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* 차트 */}
      <div id="chart">
        <ApexCharts
          options={options}
          series={series}
          type="line"
          height={350}
        />
      </div>
    </Box>
  );
};

export default TasteTime;
