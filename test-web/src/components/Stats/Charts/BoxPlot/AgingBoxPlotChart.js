import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import CircularProgress from '@mui/material/CircularProgress';
import { Box, FormControl, InputLabel, Select, MenuItem, Typography } from '@mui/material';

const AgingBoxPlotChart = ({
  startDate,
  endDate,
  animalType,
  grade,
  meatState,
  dataType,
  modality,
  meatValue,
}) => {
  const [chartData, setChartData] = useState(null);
  const [selectedLabel, setSelectedLabel] = useState('label1');
  const [loading, setLoading] = useState(true);

  // 선택 가능한 레이블들 (5개)
  const availableLabels = [
    { value: 'label1', name: '단백질 함량' },
    { value: 'label2', name: '지방 함량' },
    { value: 'label3', name: '수분 함량' },
    { value: 'label4', name: 'pH 값' },
    { value: 'label5', name: '색도 값' },
  ];

  // 숙성도 옵션
  const agingDays = [0, 7];

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // 실제 API 호출 부분 (임시로 더미 데이터 사용)
        // const response = await fetchAgingData(startDate, endDate, animalType, grade);
        // const data = await response.json();
        
        // 임시 더미 데이터 (실제 구현 시 제거)
        // 데이터 타입(관능/예측)과 측정 소스(MSI/RGB)에 따라 값이 달라지도록 분기
        const dummyDataSensory = {
          label1: {
            0: [12.5, 13.2, 12.8, 13.0, 12.7, 13.1, 12.9, 12.6, 13.3, 12.4],
            7: [13.8, 14.2, 13.9, 14.1, 13.7, 14.0, 13.6, 14.3, 13.5, 13.8]
          },
          label2: {
            0: [8.2, 8.5, 8.1, 8.3, 8.0, 8.4, 8.2, 8.6, 8.1, 8.3],
            7: [7.8, 7.5, 7.9, 7.6, 8.0, 7.7, 7.9, 7.4, 7.8, 7.6]
          },
          label3: {
            0: [65.2, 64.8, 65.5, 64.9, 65.1, 64.7, 65.3, 64.6, 65.0, 64.8],
            7: [63.5, 63.9, 63.2, 63.8, 63.6, 64.0, 63.4, 63.7, 63.3, 63.9]
          },
          label4: {
            0: [5.6, 5.7, 5.5, 5.8, 5.6, 5.7, 5.5, 5.8, 5.6, 5.7],
            7: [5.9, 6.0, 5.8, 6.1, 5.9, 6.0, 5.8, 6.1, 5.9, 6.0]
          },
          label5: {
            0: [45.2, 46.1, 44.8, 45.9, 45.5, 46.0, 44.9, 45.8, 45.3, 45.7],
            7: [42.1, 42.8, 41.9, 42.5, 42.3, 42.7, 41.8, 42.6, 42.2, 42.4]
          }
        };
        const dummyDataPred = {
          label1: {
            0: [12.1, 12.9, 12.4, 12.6, 12.3, 12.8, 12.5, 12.2, 12.7, 12.0],
            7: [13.2, 13.6, 13.3, 13.5, 13.1, 13.4, 13.0, 13.7, 13.0, 13.2]
          },
          label2: {
            0: [8.0, 8.2, 7.9, 8.1, 7.8, 8.0, 8.1, 8.3, 7.9, 8.1],
            7: [7.6, 7.3, 7.7, 7.4, 7.8, 7.5, 7.7, 7.2, 7.6, 7.4]
          },
          label3: {
            0: [65.0, 64.6, 65.3, 64.7, 64.9, 64.5, 65.1, 64.4, 64.8, 64.6],
            7: [63.3, 63.7, 63.0, 63.6, 63.4, 63.8, 63.2, 63.5, 63.1, 63.7]
          },
          label4: {
            0: [5.5, 5.6, 5.4, 5.7, 5.5, 5.6, 5.4, 5.7, 5.5, 5.6],
            7: [5.8, 5.9, 5.7, 6.0, 5.8, 5.9, 5.7, 6.0, 5.8, 5.9]
          },
          label5: {
            0: [45.0, 45.9, 44.6, 45.7, 45.3, 45.8, 44.7, 45.6, 45.1, 45.5],
            7: [41.9, 42.6, 41.7, 42.3, 42.1, 42.5, 41.6, 42.4, 42.0, 42.2]
          }
        };
        const selectedDummy = dataType === 'sensory' ? dummyDataSensory : dummyDataPred;
        setChartData(selectedDummy);
      } catch (error) {
        console.error('Error fetching aging data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate, animalType, grade]);

  // BoxPlot 통계 계산 함수
  const calculateBoxPlotStats = (values) => {
    if (!values || values.length === 0) return [];
    
    const sorted = [...values].sort((a, b) => a - b);
    const q1 = sorted[Math.floor(sorted.length * 0.25)];
    const q2 = sorted[Math.floor(sorted.length * 0.5)];
    const q3 = sorted[Math.floor(sorted.length * 0.75)];
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    
    return [min, q1, q2, q3, max];
  };

  const chartOptions = {
    chart: {
      type: 'boxPlot',
      height: 350,
      toolbar: {
        show: true,
        tools: {
          download: true,
          selection: true,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: true,
          reset: true,
        }
      }
    },
    title: {
      text: `[${modality}] 숙성도에 따른 ${availableLabels.find(l => l.value === selectedLabel)?.name} 분포 (${dataType === 'sensory' ? '관능' : '예측'})`,
      align: 'center',
      style: {
        fontSize: '16px',
        fontWeight: 'bold'
      }
    },
    xaxis: {
      categories: ['0일', '7일'],
      title: {
        text: '숙성 기간 (일)',
        style: {
          fontSize: '14px',
          fontWeight: '600'
        }
      }
    },
    yaxis: {
      title: {
        text: availableLabels.find(l => l.value === selectedLabel)?.name,
        style: {
          fontSize: '14px',
          fontWeight: '600'
        }
      }
    },
    plotOptions: {
      boxPlot: {
        colors: {
          upper: '#00E396',
          lower: '#008FFB'
        }
      }
    },
    tooltip: {
      y: {
        formatter: function (val) {
          return val.toFixed(2);
        }
      }
    },
    grid: {
      borderColor: '#e7e7e7',
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5
      }
    }
  };

  const renderChart = () => {
    if (!chartData || loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height="350px">
          <CircularProgress />
        </Box>
      );
    }

    const selectedLabelData = chartData[selectedLabel];
    if (!selectedLabelData) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height="350px">
          <Typography variant="h6" color="textSecondary">
            선택된 레이블에 대한 데이터가 없습니다.
          </Typography>
        </Box>
      );
    }

    const series = [
      {
        name: availableLabels.find(l => l.value === selectedLabel)?.name,
        type: 'boxPlot',
        data: [
          {
            x: '0일',
            y: calculateBoxPlotStats(selectedLabelData[0])
          },
          {
            x: '7일',
            y: calculateBoxPlotStats(selectedLabelData[7])
          }
        ]
      }
    ];

    return (
      <ApexCharts
        series={series}
        options={chartOptions}
        type="boxPlot"
        height={350}
      />
    );
  };

  return (
    <Box>
      {/* 레이블 선택 드롭다운 */}
      <Box mb={2}>
        <FormControl fullWidth size="small">
          <InputLabel id="label-select-label">분석할 레이블 선택</InputLabel>
          <Select
            labelId="label-select-label"
            id="label-select"
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
      {renderChart()}
    </Box>
  );
};

export default AgingBoxPlotChart;
