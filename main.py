import json
import os
import yfinance as yf  # biblioteka do pobierania danych rynkowych

# Ścieżka do pliku z portfelem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(BASE_DIR, "portfolio.json")

def load_portfolio():
    """Wczytuje portfel z JSON; obsługuje pusty/uszkodzony plik."""
    if not os.path.exists(FILENAME):
        return []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                return []
            return json.loads(text)
    except json.JSONDecodeError:
        print("⚠️  portfolio.json ma błędny format – inicjalizuję pusty portfel.")
        return []

def save_portfolio(portfolio):
    """Zapisuje portfel do pliku JSON."""
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, indent=4, ensure_ascii=False)
        f.write("\n")

def add_investment(portfolio):
    """Dodaje inwestycję do portfela."""
    name = input("Podaj nazwę aktywa: ")
    ticker = input("Podaj ticker (np. AAPL, MSFT, BTC-USD): ").upper()
    quantity = float(input("Podaj ilość jednostek: "))
    buy_price = float(input("Podaj cenę zakupu za jednostkę: "))
    portfolio.append({
        "name": name,
        "ticker": ticker,
        "quantity": quantity,
        "buy_price": buy_price,
        "current_price": buy_price
    })
    print("✅ Inwestycja dodana.")

def fetch_price(ticker):
    """Pobiera aktualną cenę z Yahoo Finance."""
    try:
        data = yf.Ticker(ticker)
        price = data.history(period="1d")["Close"].iloc[-1]
        return float(price)
    except Exception as e:
        print(f"⚠️ Nie udało się pobrać ceny dla {ticker}: {e}")
        return None

def update_price(portfolio):
    """Aktualizuje cenę rynkową z API Yahoo Finance."""
    ticker = input("Podaj ticker do aktualizacji: ").upper()
    for investment in portfolio:
        if investment.get("ticker", "").upper() == ticker:
            price = fetch_price(ticker)
            if price:
                investment["current_price"] = price
                print(f"📈 Cena {ticker} zaktualizowana: {price:.2f} USD")
            return
    print("⚠️ Nie znaleziono aktywa o podanym tickerze w portfelu.")

def show_portfolio(portfolio):
    """Wyświetla portfel inwestycyjny."""
    if not portfolio:
        print("📂 Portfel jest pusty.")
        return
    total_value = 0
    print("\n--- Twój portfel ---")
    for investment in portfolio:
        value = investment["quantity"] * investment["current_price"]
        profit = value - (investment["quantity"] * investment["buy_price"])
        percent = (profit / (investment["quantity"] * investment["buy_price"])) * 100
        total_value += value
        print(f"{investment['name']} ({investment.get('ticker','-')}): {investment['quantity']} szt. "
              f"kupione po {investment['buy_price']} USD, "
              f"teraz {investment['current_price']:.2f} USD "
              f"(Zysk/Strata: {profit:.2f} USD / {percent:.2f}%)")
    print(f"💰 Wartość całkowita portfela: {total_value:.2f} USD")

def main():
    """Główna pętla programu."""
    portfolio = load_portfolio()
    while True:
        print("\n=== Aplikacja Portfel Inwestycyjny ===")
        print("1. Dodaj inwestycję")
        print("2. Aktualizuj cenę z API")
        print("3. Pokaż portfel")
        print("4. Wyjście")
        choice = input("Wybierz opcję: ")
        if choice == "1":
            add_investment(portfolio)
            save_portfolio(portfolio)
        elif choice == "2":
            update_price(portfolio)
            save_portfolio(portfolio)
        elif choice == "3":
            show_portfolio(portfolio)
        elif choice == "4":
            save_portfolio(portfolio)
            print("👋 Do zobaczenia!")
            break
        else:
            print("⚠️ Nieprawidłowy wybór.")

if __name__ == "__main__":
    main()
