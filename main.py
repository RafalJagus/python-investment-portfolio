import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PORTFOLIO_FILE = "portfolio.json"

# ---------- Portfolio Handling ----------
def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    with open(PORTFOLIO_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

portfolio = load_portfolio()

# ---------- GUI Functions ----------
def add_investment():
    ticker = ticker_entry.get().upper()
    quantity = quantity_entry.get()
    if not ticker or not quantity.isdigit():
        messagebox.showerror("Error", "Invalid input")
        return
    
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch price: {e}")
        return

    investment = {"ticker": ticker, "quantity": int(quantity), "price": float(price)}
    portfolio.append(investment)
    save_portfolio(portfolio)
    update_portfolio_view()
    update_last_update_time()

def update_portfolio_view():
    for row in tree.get_children():
        tree.delete(row)

    total_value = 0
    for inv in portfolio:
        try:
            price = yf.Ticker(inv["ticker"]).history(period="1d")["Close"].iloc[-1]
            inv["price"] = float(price)
        except:
            price = inv.get("price", 0)

        value = inv["quantity"] * inv["price"]
        total_value += value
        tree.insert("", "end", values=(inv["ticker"], inv["quantity"], f"{inv['price']:.2f}", f"{value:.2f}"))

    total_label.config(text=f"💰 Total Portfolio Value: {total_value:.2f} USD")
    save_portfolio(portfolio)

def refresh_prices():
    update_portfolio_view()
    update_last_update_time()

def update_last_update_time():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_update_label.config(text=f"Last update: {now}")

def show_chart():
    if not portfolio:
        messagebox.showinfo("Info", "Portfolio is empty.")
        return
    
    total_history = {}

    for inv in portfolio:
        try:
            data = yf.Ticker(inv["ticker"]).history(period="6mo")
            values = data["Close"] * inv["quantity"]
            for date, val in values.items():
                total_history[date] = total_history.get(date, 0) + val
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load chart data for {inv['ticker']}: {e}")
    
    if not total_history:
        messagebox.showinfo("Info", "No data available for chart.")
        return

    # sort dates
    dates = sorted(total_history.keys())
    values = [total_history[d] for d in dates]

    # matplotlib figure
    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    ax.plot(dates, values, marker="o", linestyle="-", color="cyan")
    ax.set_title("📈 Portfolio Value Over Time (last 6 months)", color="white")
    ax.set_xlabel("Date", color="white")
    ax.set_ylabel("Portfolio Value (USD)", color="white")
    ax.tick_params(colors="white")
    ax.grid(True, linestyle="--", alpha=0.6)

    # dark background
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#2d2d2d")

    # clear previous chart if exists
    for widget in chart_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Investment Portfolio Manager")
root.configure(bg="#1e1e1e")
root.geometry("900x700")

# Input frame
input_frame = tk.Frame(root, bg="#1e1e1e")
input_frame.pack(pady=10)

tk.Label(input_frame, text="Ticker:", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5)
ticker_entry = tk.Entry(input_frame, bg="#2d2d2d", fg="white", insertbackground="white")
ticker_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Quantity:", fg="white", bg="#1e1e1e").grid(row=0, column=2, padx=5)
quantity_entry = tk.Entry(input_frame, bg="#2d2d2d", fg="white", insertbackground="white")
quantity_entry.grid(row=0, column=3, padx=5)

button_style = {
    "bg": "#2d2d2d",
    "fg": "white",
    "activebackground": "#3e3e3e",
    "activeforeground": "white",
    "relief": "flat",
    "width": 20,
    "padx": 5,
    "pady": 5
}

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Add Investment", command=add_investment, **button_style).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Refresh Prices", command=refresh_prices, **button_style).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Show Chart", command=show_chart, **button_style).grid(row=0, column=2, padx=5)

# Table
columns = ("Ticker", "Quantity", "Price", "Value")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
tree.pack(pady=10, fill=tk.BOTH, expand=True)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
    background="#2d2d2d",
    foreground="white",
    fieldbackground="#2d2d2d",
    rowheight=25
)
style.configure("Treeview.Heading",
    background="#1e1e1e",
    foreground="white"
)
style.map("Treeview",
    background=[("selected", "#4a90e2")],
    foreground=[("selected", "white")]
)

# Total & last update
total_label = tk.Label(root, text="💰 Total Portfolio Value: 0.00 USD",
                       font=("Arial", 14), bg="#1e1e1e", fg="white")
total_label.pack(pady=5)

last_update_label = tk.Label(root, text="Last update: -",
                             font=("Arial", 10), fg="gray", bg="#1e1e1e")
last_update_label.pack(pady=5)

# Chart frame
chart_frame = tk.Frame(root, bg="#1e1e1e")
chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Initial load
update_portfolio_view()
update_last_update_time()

root.mainloop()
