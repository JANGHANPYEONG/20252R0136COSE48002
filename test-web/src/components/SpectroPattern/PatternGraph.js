import React from 'react';
import ReactApexChart from 'react-apexcharts';

const PatternGraph = ({ data, peaks, onPeakClick }) => {
    // 막대 색상: peak 구간만 강조
    const barColors = data.x.map((_, i) =>
        peaks.includes(i) ? '#1976d2' : '#90caf9'
    );

    const series = [
        {
            name: '강도',
            type: 'column',
            data: data.y,
        },
        {
            name: '라인',
            type: 'line',
            data: data.y,
        },
    ];

    const options = {
        chart: {
            height: 300,
            type: 'line',
            toolbar: { show: false },
            animations: { enabled: false },
            events: {
                dataPointSelection: (event, chartContext, config) => {
                    if (peaks.includes(config.dataPointIndex)) {
                        onPeakClick(config.dataPointIndex);
                    }
                },
            },
        },
        stroke: {
            width: [0, 3],
        },
        plotOptions: {
            bar: {
                columnWidth: '60%',
                distributed: true,
            },
        },
        colors: [barColors, '#1976d2'],
        xaxis: {
            categories: data.x.map(x => `${x}nm`),
            title: { text: '파장(nm)' },
        },
        yaxis: {
            title: { text: '강도' },
        },
        legend: { show: true },
        tooltip: { shared: true },
    };

    return (
        <ReactApexChart
            options={options}
            series={series}
            type="line"
            height={300}
        />
    );
};

export default PatternGraph; 