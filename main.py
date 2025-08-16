import json
import os
import yfinance as yf
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from datetime import datetime

# --- PATH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(BASE_DIR, "portfolio.json")

# --- DATA HANDLING ---
def load_portfolio():
    if not os.path.exists(FILENAME):
        return []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                return []
            return json.loads(text)
    except json.JSONDecodeError:
        messagebox.showwarning("Warning", "portfolio.json is corrupted. Starting empty.")
        return []

def save_portfolio(portfolio):
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, indent=4, ensure_ascii=False)

def fetch_price(ticker):
    try:
        data = yf.Ticker(ticker)
        price = data.history(period="1d")["Close"].iloc[-1]
        return float(price)
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch price for {ticker}: {e}")
        return None

# --- GUI FUNCTIONS ---
def add_investment():
    name = simpledialog.askstring("Add Investment", "Asset name:")
    ticker = simpledialog.askstring("Add Investment", "Ticker (e.g., AAPL, MSFT, BTC-USD):")
    quantity = simpledialog.askfloat("Add Investment", "Quantity:")
    buy_price = simpledialog.askfloat("Add Investment", "Buy price per unit:")
    if name and ticker and quantity and buy_price:
        portfolio.append({
            "name": name,
            "ticker": ticker.upper(),
            "quantity": quantity,
            "buy_price": buy_price,
            "current_price": buy_price
        })
        save_portfolio(portfolio)
        refresh_prices()  # automatycznie odśwież po dodaniu

def refresh_prices():
    """Update all prices from Yahoo Finance API"""
    updated_any = False
    for inv in portfolio:
        price = fetch_price(inv["ticker"])
        if price:
            inv["current_price"] = price
            updated_any = True
    if updated_any:
        save_portfolio(portfolio)
        refresh_table()
        update_timestamp()

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    total_value = 0
    for inv in portfolio:
        value = inv["quantity"] * inv["current_price"]
        profit = value - (inv["quantity"] * inv["buy_price"])
        percent = (profit / (inv["quantity"] * inv["buy_price"])) * 100
        total_value += value
        tree.insert("", "end", values=(
            inv["name"],
            inv["ticker"],
            inv["quantity"],
            f"{inv['buy_price']:.2f}",
            f"{inv['current_price']:.2f}",
            f"{profit:.2f} USD",
            f"{percent:.2f}%",
            f"{value:.2f} USD"
        ))
    total_label.config(text=f"💰 Total Portfolio Value: {total_value:.2f} USD")

def update_timestamp():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_update_label.config(text=f"Last update: {now}")

# --- MAIN ---
portfolio = load_portfolio()

root = tk.Tk()
root.title("Investment Portfolio Manager")
root.geometry("950x450")

frame = tk.Frame(root)
frame.pack(pady=10)

tree = ttk.Treeview(frame, columns=(
    "Name", "Ticker", "Quantity", "Buy Price", "Current Price", "Profit", "Change %", "Value"
), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Add Investment", command=add_investment).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Refresh Prices (API)", command=refresh_prices).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Exit", command=root.quit).grid(row=0, column=2, padx=5)

total_label = tk.Label(root, text="💰 Total Portfolio Value: 0.00 USD", font=("Arial", 14))
total_label.pack(pady=5)

last_update_label = tk.Label(root, text="Last update: -", font=("Arial", 10), fg="gray")
last_update_label.pack(pady=5)

# Initial refresh on startup
refresh_prices()

root.mainloop()
