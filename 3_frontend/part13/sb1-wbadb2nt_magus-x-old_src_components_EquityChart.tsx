import React, { useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface EquityChartProps {
  data: Array<{ timestamp: Date; value: number }>;
  targetCapital: number;
  initialCapital: number;
}

export default function EquityChart({ data, targetCapital, initialCapital }: EquityChartProps) {
  const chartRef = useRef<ChartJS>(null);

  const chartData = {
    labels: data.map(d => d.timestamp.toLocaleTimeString()),
    datasets: [
      {
        label: 'Equity',
        data: data.map(d => d.value),
        fill: true,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4
      },
      {
        label: 'Target',
        data: Array(data.length).fill(targetCapital),
        borderColor: 'rgba(255, 99, 132, 0.8)',
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0
      },
      {
        label: 'Initial Capital',
        data: Array(data.length).fill(initialCapital),
        borderColor: 'rgba(54, 162, 235, 0.8)',
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Equity Curve'
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: (context: any) => {
            return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Equity (AED)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Time'
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="h-[400px]">
        <Line data={chartData} options={options} ref={chartRef} />
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-sm text-gray-600">Initial Capital</p>
          <p className="text-lg font-semibold">{initialCapital} AED</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Current Equity</p>
          <p className="text-lg font-semibold">
            {data[data.length - 1]?.value.toFixed(2)} AED
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Target</p>
          <p className="text-lg font-semibold">{targetCapital} AED</p>
        </div>
      </div>
    </div>
  );
}