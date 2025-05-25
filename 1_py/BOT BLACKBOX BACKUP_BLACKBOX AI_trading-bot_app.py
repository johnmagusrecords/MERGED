import tkinter as tk
from tkinter import messagebox, scrolledtext
from src.bot import main  # Import the main function from your bot
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_bot():
    try:
        messagebox.showinfo("Info", "Trading bot started!")
        logging.info("Trading bot started.")
        main()  # Call the main function of the bot
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        logging.error(f"Error starting bot: {str(e)}")

def stop_bot():
    messagebox.showinfo("Info", "Trading bot stopped!")
    logging.info("Trading bot stopped.")

# Create the main window
root = tk.Tk()
root.title("Trading Bot Application")

# Create a start button
start_button = tk.Button(root, text="Start Trading Bot", command=start_bot, bg='green', fg='white', font=('Helvetica', 12, 'bold'))
start_button.pack(pady=20)

# Create a stop button
stop_button = tk.Button(root, text="Stop Trading Bot", command=stop_bot, bg='red', fg='white', font=('Helvetica', 12, 'bold'))
stop_button.pack(pady=20)

# Set the background color of the main window
root.configure(bg='lightblue')


# Create a frame for displaying trades
trade_frame = tk.Frame(root, bg='lightblue')
trade_frame.pack(pady=20)

# Create labels for trade information
tk.Label(trade_frame, text="Open Trades", bg='lightblue', font=('Helvetica', 14, 'bold')).pack()

# Create a text area for displaying trades
trade_area = scrolledtext.ScrolledText(trade_frame, width=50, height=10, bg='white', fg='black', font=('Helvetica', 10))
trade_area.pack(pady=10)

# Create a label for capital amount
capital_label = tk.Label(root, text="Capital Amount: $10000", bg='lightblue', font=('Helvetica', 12))
capital_label.pack(pady=10)

# Create a text area for logs
log_area = scrolledtext.ScrolledText(root, width=50, height=10, bg='white', fg='black', font=('Helvetica', 10))
log_area.pack(pady=20)



# Run the application
root.mainloop()
