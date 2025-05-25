// MAGUS PRIME X Dashboard Integration
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Chart.js
  const ctx = document.getElementById("performanceChart").getContext("2d");

  // Helper functions
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  }

  function calculateWinRate(trades) {
    const completedTrades = trades.filter(
      (t) => t.result === "WIN" || t.result === "LOSS",
    );
    const wins = completedTrades.filter((t) => t.result === "WIN").length;
    const total = completedTrades.length;
    return total > 0 ? ((wins / total) * 100).toFixed(2) : "0.00";
  }

  function calculatePnL(trades) {
    let pnl = 0;
    for (const t of trades) {
      if (t.result === "WIN") {
        pnl += parseFloat(t.profit || 0);
      } else if (t.result === "LOSS") {
        pnl -= Math.abs(parseFloat(t.loss || 0));
      }
    }
    return pnl.toFixed(2);
  }

  // Create the performance chart
  let performanceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Take Profit",
          data: [],
          borderColor: "rgb(75, 192, 75)",
          tension: 0.3,
          fill: false,
        },
        {
          label: "Stop Loss",
          data: [],
          borderColor: "rgb(255, 99, 132)",
          tension: 0.3,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
        },
      },
      maintainAspectRatio: false,
    },
  });

  // Strategy change handler
  document.querySelectorAll(".strategy-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const strategy = this.getAttribute("data-strategy");

      fetch("/api/strategy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ strategy: strategy }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Update UI
            document.querySelectorAll(".strategy-btn").forEach((btn) => {
              btn.classList.remove("bg-green-600", "bg-blue-600", "bg-red-600");
              btn.classList.add("bg-gray-500");
            });

            this.classList.remove("bg-gray-500");
            if (strategy === "Safe") {
              this.classList.add("bg-green-600");
            } else if (strategy === "Balanced") {
              this.classList.add("bg-blue-600");
            } else if (strategy === "Aggressive") {
              this.classList.add("bg-red-600");
            }

            document.getElementById("strategy-display").textContent = strategy;
          }
        })
        .catch((err) => console.error("Error changing strategy:", err));
    });
  });

  // Clear history handler
  document
    .getElementById("clear-history-btn")
    .addEventListener("click", function () {
      if (confirm("Are you sure you want to clear trade history?")) {
        fetch("/api/clear-history", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              // Update table
              document.getElementById("trade-table-body").innerHTML =
                '<tr><td colspan="6" class="text-center py-4 text-gray-500">No trades found</td></tr>';

              // Update chart
              performanceChart.data.labels = [];
              performanceChart.data.datasets[0].data = [];
              performanceChart.data.datasets[1].data = [];
              performanceChart.update();

              // Update summary
              document.getElementById("trade-count").textContent = "0";
              document.getElementById("win-rate").textContent = "0.00%";
              document.getElementById("net-pnl").textContent = "$0.00";
            }
          })
          .catch((err) => console.error("Error clearing history:", err));
      }
    });

  // Function to refresh data
  function refreshData() {
    Promise.all([
      fetch("/api/trades").then((res) => res.json()),
      fetch("/api/metrics").then((res) => res.json()),
    ])
      .then(([trades, metrics]) => {
        // Update chart data
        performanceChart.data.labels = trades.map((t) => t.time);
        performanceChart.data.datasets[0].data = trades.map((t) =>
          parseFloat(t.tp || 0),
        );
        performanceChart.data.datasets[1].data = trades.map((t) =>
          parseFloat(t.sl || 0),
        );
        performanceChart.update();

        // Update trade table
        const tableBody = document.getElementById("trade-table-body");
        if (trades.length > 0) {
          tableBody.innerHTML = trades
            .map(
              (t, idx) => `
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <td class="py-2">${t.time}</td>
            <td>${t.symbol}</td>
            <td class="text-center ${t.direction === "BUY" ? "text-green-500" : "text-red-500"}">
              ${t.direction}
            </td>
            <td class="text-center text-green-500">${t.tp || "N/A"}</td>
            <td class="text-center text-red-500">${t.sl || "N/A"}</td>
            <td class="text-center ${
              t.result === "WIN"
                ? "text-green-500"
                : t.result === "LOSS"
                  ? "text-red-500"
                  : "text-gray-500"
            }">
              ${t.result || "OPEN"}
            </td>
          </tr>
        `,
            )
            .join("");
        } else {
          tableBody.innerHTML =
            '<tr><td colspan="6" class="text-center py-4 text-gray-500">No trades found</td></tr>';
        }

        // Update summary
        document.getElementById("trade-count").textContent = trades.length;
        const winRate = calculateWinRate(trades);
        document.getElementById("win-rate").textContent = winRate + "%";
        document.getElementById("win-rate").className =
          parseFloat(winRate) > 50 ? "text-green-500" : "text-red-500";

        const pnl = calculatePnL(trades);
        document.getElementById("net-pnl").textContent = "$" + pnl;
        document.getElementById("net-pnl").className =
          parseFloat(pnl) > 0 ? "text-green-500" : "text-red-500";

        // Update status
        if (metrics) {
          document.getElementById("bot-status").textContent = metrics.paused
            ? "Paused"
            : "Running";
          document.getElementById("bot-status").className = metrics.paused
            ? "text-red-500"
            : "text-green-500";
          document.getElementById("strategy-display").textContent =
            metrics.strategy;
          document.getElementById("interval-display").textContent =
            metrics.interval || "5 min";
        }
      })
      .catch((err) => console.error("Error refreshing data:", err));
  }

  // Initial data load
  refreshData();

  // Set up auto-refresh every 30 seconds
  setInterval(refreshData, 30000);
});
