import { Card, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { useEffect, useState } from "react"
import { Line } from "react-chartjs-2"
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js"

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend)

export default function MagusPrimeDashboard() {
  const [trades, setTrades] = useState([])
  const [botStatus, setBotStatus] = useState({
    status: "Running",
    strategy: "Balanced",
    interval: "5 min"
  })

  useEffect(() => {
    // Fetch trade history
    fetch("/api/trades")
      .then((res) => res.json())
      .then((data) => setTrades(data))
      .catch(err => console.error("Error fetching trade data:", err));
    
    // Fetch bot status
    fetch("/api/metrics")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.strategy) {
          setBotStatus({
            status: data.paused ? "Paused" : "Running",
            strategy: data.strategy,
            interval: data.interval || "5 min"
          });
        }
      })
      .catch(err => console.error("Error fetching metrics:", err));
      
    // Set up auto-refresh every 30 seconds
    const refreshInterval = setInterval(() => {
      fetch("/api/trades")
        .then((res) => res.json())
        .then((data) => setTrades(data))
        .catch(err => console.error("Error refreshing trade data:", err));
    }, 30000);
    
    return () => clearInterval(refreshInterval);
  }, [])

  const labels = trades.map((t) => t.time)
  const tpData = trades.map((t) => parseFloat(t.tp || 0))
  const slData = trades.map((t) => parseFloat(t.sl || 0))

  const chartData = {
    labels,
    datasets: [
      {
        label: "Take Profit",
        data: tpData,
        borderColor: "green",
        tension: 0.3
      },
      {
        label: "Stop Loss",
        data: slData,
        borderColor: "red",
        tension: 0.3
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: false,
      }
    },
    maintainAspectRatio: false
  };

  const handleStrategyChange = (strategy) => {
    fetch("/api/strategy", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ strategy }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          setBotStatus(prev => ({ ...prev, strategy }));
        }
      })
      .catch(err => console.error("Error changing strategy:", err));
  };

  return (
    <div className="p-4 grid gap-4 grid-cols-1 md:grid-cols-2">
      <Card className="col-span-2">
        <CardContent>
          <h2 className="text-xl font-bold mb-4">📊 MAGUS PRIME X Trade Performance</h2>
          <div style={{ height: "300px" }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">🔍 Bot Status</h3>
          <p>
            <span className="font-bold">Status:</span> 
            <span className={botStatus.status === "Running" ? "text-green-500" : "text-red-500"}>
              {" "}{botStatus.status}
            </span>
          </p>
          <p><span className="font-bold">Strategy:</span> {botStatus.strategy}</p>
          <p><span className="font-bold">Interval:</span> {botStatus.interval}</p>
          <div className="mt-4 flex space-x-2">
            <Button 
              className={`text-xs ${botStatus.strategy === "Safe" ? "bg-green-600" : "bg-gray-500"}`}
              onClick={() => handleStrategyChange("Safe")}
            >
              Safe
            </Button>
            <Button 
              className={`text-xs ${botStatus.strategy === "Balanced" ? "bg-blue-600" : "bg-gray-500"}`}
              onClick={() => handleStrategyChange("Balanced")}
            >
              Balanced
            </Button>
            <Button 
              className={`text-xs ${botStatus.strategy === "Aggressive" ? "bg-red-600" : "bg-gray-500"}`}
              onClick={() => handleStrategyChange("Aggressive")}
            >
              Aggressive
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">📈 Summary</h3>
          <p><span className="font-bold">Trades:</span> {trades.length}</p>
          <p>
            <span className="font-bold">Win Rate:</span>{" "}
            <span className={parseFloat(calculateWinRate(trades)) > 50 ? "text-green-500" : "text-red-500"}>
              {calculateWinRate(trades)}%
            </span>
          </p>
          <p>
            <span className="font-bold">Net PnL:</span>{" "}
            <span className={parseFloat(calculatePnL(trades)) > 0 ? "text-green-500" : "text-red-500"}>
              ${calculatePnL(trades)}
            </span>
          </p>
          <div className="mt-4">
            <Button 
              className="text-xs bg-red-500 hover:bg-red-600"
              onClick={() => {
                if (confirm("Are you sure you want to clear trade history?")) {
                  fetch("/api/clear-history", { method: "POST" })
                    .then(response => response.json())
                    .then(data => {
                      if (data.success) {
                        setTrades([]);
                      }
                    })
                    .catch(err => console.error("Error clearing history:", err));
                }
              }}
            >
              Clear History
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-2">
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">🧾 Trade Log</h3>
          <div className="max-h-[300px] overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-white dark:bg-gray-800">
                <tr>
                  <th className="text-left">Time</th>
                  <th className="text-left">Symbol</th>
                  <th className="text-center">Action</th>
                  <th className="text-center">TP</th>
                  <th className="text-center">SL</th>
                  <th className="text-center">Result</th>
                </tr>
              </thead>
              <tbody>
                {trades.length > 0 ? (
                  trades.map((t, idx) => (
                    <tr key={idx} className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-2">{t.time}</td>
                      <td>{t.symbol}</td>
                      <td className={`text-center ${t.direction === "BUY" ? "text-green-500" : "text-red-500"}`}>
                        {t.direction}
                      </td>
                      <td className="text-center text-green-500">{t.tp || 'N/A'}</td>
                      <td className="text-center text-red-500">{t.sl || 'N/A'}</td>
                      <td className={`text-center ${
                        t.result === "WIN" ? "text-green-500" : 
                        t.result === "LOSS" ? "text-red-500" : "text-gray-500"
                      }`}>
                        {t.result || 'OPEN'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="text-center py-4 text-gray-500">
                      No trades found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function calculateWinRate(trades) {
  const completedTrades = trades.filter(t => t.result === "WIN" || t.result === "LOSS");
  const wins = completedTrades.filter((t) => t.result === "WIN").length;
  const total = completedTrades.length;
  return total > 0 ? ((wins / total) * 100).toFixed(2) : "0.00";
}

function calculatePnL(trades) {
  let pnl = 0;
  for (const t of trades) {
    if (t.result === "WIN") {
      // For winning trades, add the profit (difference between entry and TP)
      pnl += parseFloat(t.profit || 0);
    } else if (t.result === "LOSS") {
      // For losing trades, subtract the loss (difference between entry and SL)
      pnl -= Math.abs(parseFloat(t.loss || 0));
    }
  }
  return pnl.toFixed(2);
}
