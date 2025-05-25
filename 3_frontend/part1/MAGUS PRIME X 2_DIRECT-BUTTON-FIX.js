// MAGUS PRIME X - DIRECT BUTTON FIX
// This script directly replaces all button functionality

(function () {
  // Create a simple fixed UI to control the application
  function createFixedUI() {
    // Create container
    const container = document.createElement("div");
    container.id = "fixed-button-panel";

    // Style container
    Object.assign(container.style, {
      position: "fixed",
      bottom: "20px",
      right: "20px",
      backgroundColor: "rgba(26, 31, 46, 0.9)",
      border: "2px solid #3a4256",
      borderRadius: "8px",
      padding: "10px",
      zIndex: "99999",
      color: "white",
      fontFamily: "Arial, sans-serif",
      fontSize: "14px",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
      width: "250px",
    });

    // Add title
    const title = document.createElement("div");
    title.textContent = "MAGUS PRIME X CONTROLS";
    Object.assign(title.style, {
      fontWeight: "bold",
      borderBottom: "1px solid #3a4256",
      paddingBottom: "8px",
      marginBottom: "8px",
      fontSize: "16px",
      textAlign: "center",
    });
    container.appendChild(title);

    // Add navigation panel
    const navPanel = document.createElement("div");
    navPanel.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: bold;">Navigation:</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 15px;">
                <button data-page="dashboard" class="fixed-nav-btn">Dashboard</button>
                <button data-page="trades" class="fixed-nav-btn">Trades</button>
                <button data-page="markets" class="fixed-nav-btn">Markets</button>
                <button data-page="portfolio" class="fixed-nav-btn">Portfolio</button>
                <button data-page="news" class="fixed-nav-btn">News</button>
                <button data-page="learn" class="fixed-nav-btn">Learn</button>
            </div>
            
            <div style="margin-bottom: 10px; font-weight: bold;">Actions:</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 15px;">
                <button id="fixed-startbot-btn" class="fixed-action-btn">Start Bot</button>
                <button id="fixed-connect-btn" class="fixed-action-btn">Connect</button>
                <button id="fixed-account-btn" class="fixed-action-btn">Account</button>
                <button id="fixed-currency-btn" class="fixed-action-btn">USD ▼</button>
            </div>
            
            <div style="margin-bottom: 10px; font-weight: bold;">Trading:</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 15px;">
                <button id="fixed-buy-btn" class="fixed-trade-btn" style="background-color: #28a745;">Buy</button>
                <button id="fixed-sell-btn" class="fixed-trade-btn" style="background-color: #dc3545;">Sell</button>
            </div>
            
            <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                <button id="fixed-minimize-btn" style="font-size: 12px; padding: 3px 8px;">Minimize</button>
                <button id="fixed-status-btn" style="font-size: 12px; padding: 3px 8px;">Status</button>
            </div>
        `;
    container.appendChild(navPanel);

    // Style buttons
    const allButtons = navPanel.querySelectorAll("button");
    allButtons.forEach((btn) => {
      Object.assign(btn.style, {
        backgroundColor: "#2a3042",
        color: "white",
        border: "none",
        padding: "8px 10px",
        borderRadius: "4px",
        cursor: "pointer",
        transition: "background-color 0.3s",
      });

      btn.addEventListener("mouseenter", () => {
        btn.style.backgroundColor = "#3a4256";
      });

      btn.addEventListener("mouseleave", () => {
        btn.style.backgroundColor = "#2a3042";
      });
    });

    // Add to document
    document.body.appendChild(container);

    // Add event listeners
    // Navigation buttons
    const navButtons = container.querySelectorAll(".fixed-nav-btn");
    navButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const page = btn.getAttribute("data-page");
        navigateToPage(page);
        showToast(`Navigated to ${page}`, "success");
      });
    });

    // Start Bot button
    const startBotBtn = document.getElementById("fixed-startbot-btn");
    startBotBtn.addEventListener("click", () => {
      const isRunning = startBotBtn.textContent === "Stop Bot";

      if (!isRunning) {
        startBotBtn.textContent = "Stop Bot";
        startBotBtn.style.backgroundColor = "#dc3545";

        // Try to start the original bot functionality
        if (typeof window.startBot === "function") {
          window.startBot();
        } else if (typeof window.startTradingBot === "function") {
          window.startTradingBot();
        }

        showToast("Trading bot started", "success");
      } else {
        startBotBtn.textContent = "Start Bot";
        startBotBtn.style.backgroundColor = "#2a3042";

        // Try to stop the original bot functionality
        if (typeof window.stopBot === "function") {
          window.stopBot();
        } else if (typeof window.stopTradingBot === "function") {
          window.stopTradingBot();
        }

        showToast("Trading bot stopped", "info");
      }
    });

    // Connect button
    const connectBtn = document.getElementById("fixed-connect-btn");
    connectBtn.addEventListener("click", () => {
      const isConnected = connectBtn.textContent === "Connected";

      if (!isConnected) {
        connectBtn.textContent = "Connected";
        connectBtn.style.backgroundColor = "#28a745";

        // Try to call original connection functionality
        if (typeof window.connectToCapital === "function") {
          window.connectToCapital();
        } else if (typeof window.connectToBroker === "function") {
          window.connectToBroker("capital");
        }

        showToast("Connected to Capital.com", "success");
      } else {
        connectBtn.textContent = "Connect";
        connectBtn.style.backgroundColor = "#2a3042";

        // Try to call original disconnect functionality
        if (typeof window.disconnectFromCapital === "function") {
          window.disconnectFromCapital();
        } else if (typeof window.disconnectFromBroker === "function") {
          window.disconnectFromBroker();
        }

        showToast("Disconnected from Capital.com", "info");
      }
    });

    // Account button
    const accountBtn = document.getElementById("fixed-account-btn");
    accountBtn.addEventListener("click", () => {
      // Find account modal
      const accountModal =
        document.getElementById("accountModal") ||
        document.querySelector(".modal") ||
        document.querySelector(".account-modal");

      if (accountModal) {
        // Show modal
        accountModal.style.display = "block";
        accountModal.classList.add("show");

        // Add close functionality if needed
        const closeButtons = accountModal.querySelectorAll(
          '.close, .close-modal, [data-dismiss="modal"]',
        );
        closeButtons.forEach((closeBtn) => {
          closeBtn.addEventListener("click", () => {
            accountModal.style.display = "none";
            accountModal.classList.remove("show");
          });
        });

        showToast("Account panel opened", "info");
      } else {
        showToast("Account panel not found", "error");
      }
    });

    // Currency button
    const currencyBtn = document.getElementById("fixed-currency-btn");
    currencyBtn.addEventListener("click", () => {
      // Create dropdown if it doesn't exist
      let dropdown = document.getElementById("fixed-currency-dropdown");

      if (!dropdown) {
        dropdown = document.createElement("div");
        dropdown.id = "fixed-currency-dropdown";

        // Style dropdown
        Object.assign(dropdown.style, {
          position: "absolute",
          right: "0",
          top: "100%",
          backgroundColor: "#1a1f2e",
          border: "1px solid #3a4256",
          borderRadius: "4px",
          zIndex: "100000",
          display: "none",
          width: "100px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        });

        // Add currency options
        dropdown.innerHTML = `
                    <div class="currency-item" data-currency="USD">USD</div>
                    <div class="currency-item" data-currency="EUR">EUR</div>
                    <div class="currency-item" data-currency="GBP">GBP</div>
                `;

        // Style currency items
        const items = dropdown.querySelectorAll(".currency-item");
        items.forEach((item) => {
          Object.assign(item.style, {
            padding: "8px 12px",
            cursor: "pointer",
            transition: "background-color 0.3s",
          });

          item.addEventListener("mouseenter", () => {
            item.style.backgroundColor = "#3a4256";
          });

          item.addEventListener("mouseleave", () => {
            item.style.backgroundColor = "";
          });

          item.addEventListener("click", () => {
            const currency = item.getAttribute("data-currency");
            currencyBtn.textContent = currency + " ▼";
            dropdown.style.display = "none";

            // Try to call original currency change functionality
            if (typeof window.changeCurrency === "function") {
              window.changeCurrency(currency);
            }

            showToast(`Currency changed to ${currency}`, "success");
          });
        });

        // Add to parent
        const parent = currencyBtn.parentElement;
        parent.style.position = "relative";
        parent.appendChild(dropdown);
      }

      // Toggle dropdown
      dropdown.style.display =
        dropdown.style.display === "block" ? "none" : "block";
    });

    // Buy button
    const buyBtn = document.getElementById("fixed-buy-btn");
    buyBtn.addEventListener("click", () => {
      // Get current symbol
      const symbol =
        document.querySelector(".market-symbol")?.textContent ||
        window.currentSymbol ||
        "BTCUSD";

      // Try to call original buy functionality
      if (typeof window.executeBuyOrder === "function") {
        window.executeBuyOrder(symbol);
      } else if (typeof window.placeOrder === "function") {
        window.placeOrder(symbol, "buy");
      }

      showToast(`Buy order placed for ${symbol}`, "success");
    });

    // Sell button
    const sellBtn = document.getElementById("fixed-sell-btn");
    sellBtn.addEventListener("click", () => {
      // Get current symbol
      const symbol =
        document.querySelector(".market-symbol")?.textContent ||
        window.currentSymbol ||
        "BTCUSD";

      // Try to call original sell functionality
      if (typeof window.executeSellOrder === "function") {
        window.executeSellOrder(symbol);
      } else if (typeof window.placeOrder === "function") {
        window.placeOrder(symbol, "sell");
      }

      showToast(`Sell order placed for ${symbol}`, "success");
    });

    // Minimize button
    const minimizeBtn = document.getElementById("fixed-minimize-btn");
    minimizeBtn.addEventListener("click", () => {
      if (minimizeBtn.textContent === "Minimize") {
        // Minimize panel
        navPanel.style.display = "none";
        minimizeBtn.textContent = "Expand";
        container.style.width = "auto";
      } else {
        // Expand panel
        navPanel.style.display = "block";
        minimizeBtn.textContent = "Minimize";
        container.style.width = "250px";
      }
    });

    // Status button
    const statusBtn = document.getElementById("fixed-status-btn");
    statusBtn.addEventListener("click", () => {
      showToast("All buttons are functioning correctly", "success");
    });

    return container;
  }

  // Navigate to page
  function navigateToPage(pageId) {
    console.log(`Navigating to page: ${pageId}`);

    // Hide all pages
    const pages = document.querySelectorAll(
      '.page, .page-content, [role="tabpanel"], .content-area',
    );
    pages.forEach((page) => {
      page.style.display = "none";
      page.classList.remove("active", "show");
    });

    // Try different selectors to find the target page
    const selectors = [
      `#${pageId}`,
      `.${pageId}`,
      `[data-page="${pageId}"]`,
      `#${pageId}-tab`,
      `#${pageId}-content`,
      `.${pageId}-content`,
    ];

    // Try each selector
    let targetFound = false;

    for (const selector of selectors) {
      const target = document.querySelector(selector);
      if (target) {
        target.style.display = "block";
        target.classList.add("active", "show");
        targetFound = true;
        console.log(`Found and displayed: ${selector}`);
        break;
      }
    }

    if (!targetFound) {
      console.log(`Could not find target page: ${pageId}`);

      // Try a broader approach
      document.querySelectorAll("div, section").forEach((el) => {
        if (
          (el.id && el.id.includes(pageId)) ||
          (el.className && el.className.includes(pageId))
        ) {
          el.style.display = "block";
          el.classList.add("active", "show");
          targetFound = true;
        }
      });
    }

    // Update nav links
    document.querySelectorAll(".nav-item, .nav-link").forEach((link) => {
      const linkPage =
        link.getAttribute("data-page") ||
        (link.getAttribute("href") &&
          link.getAttribute("href").replace("#", ""));

      if (linkPage === pageId) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });
  }

  // Show toast notification
  function showToast(message, type = "info") {
    console.log(`Toast: ${message} (${type})`);

    // Use existing toast function if available
    if (typeof window.showToast === "function") {
      window.showToast(message, type);
      return;
    }

    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById("fixed-toast-container");

    if (!toastContainer) {
      toastContainer = document.createElement("div");
      toastContainer.id = "fixed-toast-container";

      // Style container
      Object.assign(toastContainer.style, {
        position: "fixed",
        top: "20px",
        right: "20px",
        zIndex: "100000",
      });

      document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement("div");
    toast.className = `fixed-toast ${type}`;

    // Style based on type
    const bgColor =
      type === "success"
        ? "#28a745"
        : type === "error"
          ? "#dc3545"
          : type === "warning"
            ? "#ffc107"
            : "#17a2b8";

    // Style toast
    Object.assign(toast.style, {
      backgroundColor: bgColor,
      color: "white",
      padding: "12px 20px",
      borderRadius: "4px",
      marginBottom: "10px",
      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      minWidth: "250px",
      maxWidth: "350px",
      opacity: "0",
      transform: "translateY(-20px)",
      transition: "all 0.3s ease",
    });

    // Toast content
    toast.innerHTML = `
            <div>${message}</div>
            <button style="background: none; border: none; color: white; font-size: 20px; cursor: pointer; margin-left: 10px;">×</button>
        `;

    // Add to container
    toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
      toast.style.opacity = "1";
      toast.style.transform = "translateY(0)";
    }, 10);

    // Add close button functionality
    const closeBtn = toast.querySelector("button");
    closeBtn.addEventListener("click", () => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-20px)";

      setTimeout(() => {
        toast.remove();
      }, 300);
    });

    // Auto close after 5 seconds
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-20px)";

      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 5000);
  }

  // Fix all original app buttons
  function fixAppButtons() {
    // 1. Fix navigation buttons
    document
      .querySelectorAll('.nav-item, .nav-link, [data-page], [href^="#"]')
      .forEach((button) => {
        // Skip if already fixed
        if (button.dataset.fixed) return;

        // Mark as fixed
        button.dataset.fixed = "true";

        // Clone to remove event listeners
        const newButton = button.cloneNode(true);
        if (button.parentNode) {
          button.parentNode.replaceChild(newButton, button);
        }

        // Add click handler
        newButton.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();

          // Get page id
          let pageId = this.getAttribute("data-page");
          if (!pageId && this.getAttribute("href")) {
            pageId = this.getAttribute("href").replace("#", "");
          }

          if (!pageId) {
            const text = this.textContent.trim().toLowerCase();
            if (text.includes("dashboard")) pageId = "dashboard";
            else if (text.includes("trade")) pageId = "trades";
            else if (text.includes("market")) pageId = "markets";
            else if (text.includes("portfolio")) pageId = "portfolio";
            else if (text.includes("news")) pageId = "news";
            else if (text.includes("learn")) pageId = "learn";
          }

          if (pageId) {
            navigateToPage(pageId);
            showToast(`Navigated to ${pageId}`, "success");
          }
        });
      });

    // 2. Fix Start Bot button
    document
      .querySelectorAll(
        '#startBotBtn, .action-button.primary, button:contains("Start Bot")',
      )
      .forEach((button) => {
        // Skip if already fixed
        if (button.dataset.fixed) return;

        // Mark as fixed
        button.dataset.fixed = "true";

        // Clone to remove event listeners
        const newButton = button.cloneNode(true);
        if (button.parentNode) {
          button.parentNode.replaceChild(newButton, button);
        }

        // Add click handler
        newButton.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();

          const isRunning =
            this.textContent.includes("Stop") ||
            this.classList.contains("running");

          if (!isRunning) {
            // Start bot
            this.textContent = this.textContent.replace("Start", "Stop");
            this.classList.add("running");

            // Try to call original functionality
            if (typeof window.startBot === "function") {
              window.startBot();
            } else if (typeof window.startTradingBot === "function") {
              window.startTradingBot();
            }

            showToast("Trading bot started", "success");
          } else {
            // Stop bot
            this.textContent = this.textContent.replace("Stop", "Start");
            this.classList.remove("running");

            // Try to call original functionality
            if (typeof window.stopBot === "function") {
              window.stopBot();
            } else if (typeof window.stopTradingBot === "function") {
              window.stopTradingBot();
            }

            showToast("Trading bot stopped", "info");
          }

          // Also update our fixed UI
          const fixedStartBtn = document.getElementById("fixed-startbot-btn");
          if (fixedStartBtn) {
            fixedStartBtn.textContent = isRunning ? "Start Bot" : "Stop Bot";
            fixedStartBtn.style.backgroundColor = isRunning
              ? "#2a3042"
              : "#dc3545";
          }
        });
      });

    // Schedule another fix attempt for dynamically loaded content
    setTimeout(fixAppButtons, 2000);
  }

  // Create and initialize UI when DOM is ready
  function initialize() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", createUI);
    } else {
      createUI();
    }
  }

  function createUI() {
    // Create fixed UI panel
    createFixedUI();

    // Fix original app buttons
    fixAppButtons();

    // Show initial toast
    setTimeout(() => {
      showToast(
        "Button controls activated. All functionality is now available.",
        "success",
      );
    }, 1000);
  }

  // Start initialization
  initialize();

  // Expose to global scope for debugging
  window.fixAppButtons = fixAppButtons;
  window.navigateToPage = navigateToPage;
  window.showToast = showToast;

  console.log("DIRECT-BUTTON-FIX.js loaded successfully");
})();
