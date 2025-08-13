import json
import os

# ──> Zapisuj plik obok skryptu (bezpieczniej)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # katalog, w którym jest ten plik .py
FILENAME = os.path.join(BASE_DIR, "portfolio.json")

def load_portfolio():
    """Wczytuje portfel z JSON; obsługuje pusty/uszkodzony plik i pierwszy start."""
    if not os.path.exists(FILENAME):
        return []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                # pusty plik – traktujemy jak brak danych
                return []
            return json.loads(text)
    except json.JSONDecodeError:
        # plik istnieje, ale ma zły format – nie blokujemy działania aplikacji
        print("⚠️  portfolio.json jest pusty lub ma błędny format. Inicjalizuję pusty portfel.")
        return []
def save_portfolio(portfolio):
    """Zapisuje dane portfela do pliku JSON"""
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, indent=4, ensure_ascii=False)

def add_investment(portfolio):
    """Dodaje nową inwestycję do portfela"""
    name = input("Podaj nazwę aktywa: ")
    quantity = float(input("Podaj ilość jednostek: "))
    buy_price = float(input("Podaj cenę zakupu za jednostkę: "))
    portfolio.append({
        "name": name,
        "quantity": quantity,
        "buy_price": buy_price,
        "current_price": buy_price
    })
    print("✅ Inwestycja została dodana.")

def update_price(portfolio):
    """Aktualizuje bieżącą cenę rynkową dla wybranego aktywa"""
    name = input("Podaj nazwę aktywa do aktualizacji: ")
    for investment in portfolio:
        if investment["name"].lower() == name.lower():
            new_price = float(input("Podaj nową cenę rynkową: "))
            investment["current_price"] = new_price
            print("📈 Cena została zaktualizowana.")
            return
    print("⚠️ Nie znaleziono takiego aktywa.")

def show_portfolio(portfolio):
    """Wyświetla wszystkie inwestycje w portfelu wraz z zyskiem/stratą"""
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
        print(f"{investment['name']}: {investment['quantity']} szt. "
              f"kupione po {investment['buy_price']} USD, "
              f"teraz {investment['current_price']} USD "
              f"(Zysk/Strata: {profit:.2f} USD / {percent:.2f}%)")
    print(f"💰 Wartość całkowita portfela: {total_value:.2f} USD")

def main():
    """Główna pętla programu"""
    portfolio = load_portfolio()
    while True:
        print("\n=== Aplikacja Portfel Inwestycyjny ===")
        print("1. Dodaj inwestycję")
        print("2. Aktualizuj cenę")
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
