// MAGUS PRIME X - Navigation Bar Fix
// This script fixes the top navigation bar buttons

document.addEventListener("DOMContentLoaded", function () {
  console.log("MAGUS PRIME X - Navigation Bar Fix Loaded");

  // Fix for main navigation links (Dashboard, Trades, Markets, etc.)
  const navLinks = document.querySelectorAll(".nav-links .nav-link");
  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      // Get the target section from href
      const targetId = this.getAttribute("href").replace("#", "");
      console.log("Navigation clicked:", targetId);

      // Remove active class from all nav links
      navLinks.forEach((navLink) => {
        navLink.classList.remove("active");
      });

      // Add active class to clicked link
      this.classList.add("active");

      // Hide all page sections
      const pageSections = document.querySelectorAll(".page-section");
      pageSections.forEach((section) => {
        section.style.display = "none";
      });

      // Show the target section
      const targetSection =
        document.getElementById(targetId) ||
        document.querySelector(`.${targetId}-section`);
      if (targetSection) {
        targetSection.style.display = "block";
      } else {
        console.log(`Section #${targetId} not found, creating placeholder`);
        // Create a placeholder section if it doesn't exist
        const newSection = document.createElement("div");
        newSection.id = targetId;
        newSection.className = `page-section ${targetId}-section`;
        newSection.innerHTML = `<h2>${targetId.charAt(0).toUpperCase() + targetId.slice(1)}</h2><p>This section is under development.</p>`;
        document.querySelector(".container").appendChild(newSection);
        newSection.style.display = "block";
      }
    });
  });

  // Fix for Start Bot button
  const startBotBtn = document.querySelector(".action-button.primary");
  if (startBotBtn) {
    startBotBtn.addEventListener("click", function () {
      console.log("Start Bot clicked");
      this.innerHTML = '<i class="fas fa-stop"></i> Stop Bot';
      this.classList.toggle("active");

      if (this.classList.contains("active")) {
        // Start the bot logic
        showNotification("Trading bot started successfully!", "success");
      } else {
        // Stop the bot logic
        this.innerHTML = '<i class="fas fa-play"></i> Start Bot';
        showNotification("Trading bot stopped", "info");
      }
    });
  }

  // Fix for Connect button
  const connectBtn = document.getElementById("connectBtn");
  if (connectBtn) {
    connectBtn.addEventListener("click", function () {
      console.log("Connect button clicked");

      // Toggle connected state
      this.classList.toggle("connected");

      if (this.classList.contains("connected")) {
        this.innerHTML = '<i class="fas fa-check"></i> Connected';

        // Call the existing Capital.com connection logic if available
        if (
          window.connectToCapital &&
          typeof window.connectToCapital === "function"
        ) {
          window.connectToCapital();
        }

        showNotification("Connected to Capital.com successfully!", "success");
      } else {
        this.innerHTML = '<i class="fas fa-plug"></i> Connect';
        showNotification("Disconnected from trading API", "info");
      }
    });
  }

  // Fix for Account button
  const accountBtn = document.getElementById("loginBtn");
  if (accountBtn) {
    accountBtn.addEventListener("click", function () {
      console.log("Account button clicked");

      // Show the login modal
      const loginModal = document.getElementById("loginModal");
      if (loginModal) {
        loginModal.style.display = "flex";
      }
    });

    // Also fix the close button for the modal
    const closeModal = document.querySelector(".close-modal");
    if (closeModal) {
      closeModal.addEventListener("click", function () {
        document.getElementById("loginModal").style.display = "none";
      });
    }
  }

  // Fix for Currency dropdown
  const currencyDropdown = document.querySelector(
    ".dropdown .action-button.secondary",
  );
  if (currencyDropdown) {
    currencyDropdown.addEventListener("click", function () {
      console.log("Currency dropdown clicked");
      // Create dropdown menu if it doesn't exist
      let dropdownMenu = document.querySelector(".currency-dropdown-menu");

      if (!dropdownMenu) {
        dropdownMenu = document.createElement("div");
        dropdownMenu.className = "currency-dropdown-menu";
        dropdownMenu.innerHTML = `
                    <div class="dropdown-item">USD</div>
                    <div class="dropdown-item">EUR</div>
                    <div class="dropdown-item">GBP</div>
                    <div class="dropdown-item">JPY</div>
                `;

        // Insert dropdown menu after the button
        this.parentNode.appendChild(dropdownMenu);

        // Add click events to dropdown items
        dropdownMenu.querySelectorAll(".dropdown-item").forEach((item) => {
          item.addEventListener("click", function () {
            currencyDropdown.innerHTML = `
                            <i class="fas fa-dollar-sign"></i> ${this.textContent}
                            <i class="fas fa-chevron-down"></i>
                        `;
            dropdownMenu.style.display = "none";
          });
        });
      } else {
        // Toggle dropdown visibility
        dropdownMenu.style.display =
          dropdownMenu.style.display === "block" ? "none" : "block";
      }
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".dropdown")) {
        const dropdownMenu = document.querySelector(".currency-dropdown-menu");
        if (dropdownMenu) {
          dropdownMenu.style.display = "none";
        }
      }
    });
  }

  // Helper function to show notifications
  function showNotification(message, type = "info") {
    // Check if the notification function already exists
    if (
      window.showNotification &&
      typeof window.showNotification === "function"
    ) {
      window.showNotification(message, type);
      return;
    }

    // Create our own notification if one doesn't exist
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${
                  type === "success"
                    ? "fa-check-circle"
                    : type === "error"
                      ? "fa-exclamation-circle"
                      : "fa-info-circle"
                }"></i>
                <span>${message}</span>
            </div>
            <button class="close-notification">×</button>
        `;

    // Add notification to the page
    document.body.appendChild(notification);

    // Add event listener to close button
    notification
      .querySelector(".close-notification")
      .addEventListener("click", function () {
        notification.remove();
      });

    // Auto remove after 5 seconds
    setTimeout(() => {
      notification.classList.add("fade-out");
      setTimeout(() => {
        notification.remove();
      }, 500);
    }, 5000);
  }

  // Add some default CSS for notifications if they don't exist
  if (!document.querySelector("#notification-styles")) {
    const style = document.createElement("style");
    style.id = "notification-styles";
    style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #1a1f2e;
                border-left: 4px solid #3498db;
                color: white;
                padding: 15px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                min-width: 300px;
                animation: slide-in 0.5s forwards;
            }
            
            .notification.success {
                border-left-color: #2ecc71;
            }
            
            .notification.error {
                border-left-color: #e74c3c;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
            }
            
            .notification i {
                margin-right: 10px;
                font-size: 18px;
            }
            
            .close-notification {
                background: none;
                border: none;
                color: #aaa;
                font-size: 18px;
                cursor: pointer;
            }
            
            .close-notification:hover {
                color: white;
            }
            
            .notification.fade-out {
                opacity: 0;
                transform: translateX(30px);
                transition: all 0.5s;
            }
            
            .currency-dropdown-menu {
                position: absolute;
                top: 100%;
                right: 0;
                background-color: #1a1f2e;
                border: 1px solid #2d3748;
                border-radius: 4px;
                overflow: hidden;
                z-index: 1000;
                display: none;
                width: 100px;
            }
            
            .dropdown-item {
                padding: 10px 15px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .dropdown-item:hover {
                background-color: #2d3748;
            }
            
            @keyframes slide-in {
                0% {
                    transform: translateX(100px);
                    opacity: 0;
                }
                100% {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
    document.head.appendChild(style);
  }

  console.log("MAGUS PRIME X - Navigation Bar Fix Applied");
});
