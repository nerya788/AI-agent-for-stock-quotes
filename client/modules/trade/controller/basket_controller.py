import requests
from PySide6.QtCore import QObject
from PySide6.QtWidgets import (
    QTableWidgetItem,
    QSpinBox,
    QMessageBox,
    QDialog,
    QVBoxLayout,
)
from client.modules.trade.view.trade_view import TradeView
from client.modules.trade.models.trade_model import TradeModel


class BasketCheckoutDialog(QDialog):
    def __init__(self, parent, total_amount, saved_cards=None):
        super().__init__(parent)
        self.setWindowTitle("Secure Checkout - AI Basket")
        self.card_data = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Here's the trick: instantiate the TradeView you already built
        self.trade_view = TradeView()

        # Configure it for a "full basket" checkout instead of a single stock
        self.trade_view.set_mode("buy")
        self.trade_view.set_stock_data("AI Portfolio Basket", total_amount)

        # Lock the quantity so the overall total can't be altered
        self.trade_view.amount_spin.setValue(1)
        self.trade_view.amount_spin.setEnabled(False)
        self.trade_view.btn_minus.setEnabled(False)
        self.trade_view.btn_plus.setEnabled(False)

        self.trade_view.save_card_chk.setChecked(True)

        # Connect the signals
        self.trade_view.on_trade_clicked.connect(self.on_success)
        self.trade_view.on_cancel_clicked.connect(self.reject)

        layout.addWidget(self.trade_view)

    def on_success(self, trade_data):
        # After validation passes and the user clicks CONFIRM, the data arrives here
        self.card_data = trade_data
        self.accept()


class BasketController(QObject):
    def __init__(self, app, view, basket_data, total_budget):
        super().__init__()
        self.app = app
        self.view = view
        self.basket_data = basket_data
        self.total_budget = float(total_budget)
        self.rows_data = []  # Store row data for real-time calculations

        self.setup_connections()
        self.populate_table()

    def setup_connections(self):
        # Connect the dialog's cancel/confirm buttons
        self.view.cancel_btn.clicked.connect(self.view.reject)
        self.view.confirm_btn.clicked.connect(self.execute_all_trades)

    def populate_table(self):
        self.view.table.setRowCount(0)
        self.rows_data.clear()

        for item in self.basket_data:
            symbol = item.get("symbol")
            percentage = item.get("percentage", 0)

            if not symbol or percentage <= 0:
                continue

            # Fetch real-time price from our server
            price = self.fetch_price(symbol)
            if price <= 0:
                continue

            # Initial quantity based on budget
            budget_for_stock = self.total_budget * (percentage / 100.0)
            quantity = int(budget_for_stock // price)

            # Add a row to the table
            row_idx = self.view.table.rowCount()
            self.view.table.insertRow(row_idx)

            # Column 0: symbol
            self.view.table.setItem(row_idx, 0, QTableWidgetItem(symbol))

            # Column 1: price
            self.view.table.setItem(row_idx, 1, QTableWidgetItem(f"${price:.2f}"))

            # Column 2: quantity (interactive spinbox)
            spin_box = QSpinBox()
            spin_box.setRange(0, 10000)
            spin_box.setValue(quantity)
            # Update totals whenever the quantity changes
            spin_box.valueChanged.connect(self.update_totals)
            self.view.table.setCellWidget(row_idx, 2, spin_box)

            # Column 3: row total (updated later)
            self.view.table.setItem(row_idx, 3, QTableWidgetItem("$0.00"))

            # Keep a reference so we can recalculate
            self.rows_data.append(
                {
                    "symbol": symbol,
                    "price": price,
                    "spin_box": spin_box,
                    "row_idx": row_idx,
                }
            )

        # Initial totals calculation
        self.update_totals()

    def fetch_price(self, symbol):
        """Quick call to the server to fetch the latest price."""
        try:
            response = requests.get(f"http://127.0.0.1:8000/stocks/quote/{symbol}")
            if response.status_code == 200:
                return response.json().get("price", 0.0)
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
        return 0.0

    def update_totals(self):
        """Recalculate all row totals and the final total."""
        grand_total = 0.0
        for data in self.rows_data:
            qty = data["spin_box"].value()
            price = data["price"]

            row_total = qty * price
            grand_total += row_total

            # Update the row total cell
            self.view.table.setItem(
                data["row_idx"], 3, QTableWidgetItem(f"${row_total:.2f}")
            )

        # Update the final total label
        self.view.total_label.setText(f"Total Estimated Cost: ${grand_total:.2f}")

    def execute_all_trades(self):
        trades_to_execute = []
        grand_total = 0.0

        for data in self.rows_data:
            qty = data["spin_box"].value()
            if qty > 0:
                trades_to_execute.append(
                    {"symbol": data["symbol"], "amount": qty, "price": data["price"], "sector": data.get("sector", "Unknown")}
                )
                grand_total += qty * data["price"]

        if not trades_to_execute:
            QMessageBox.warning(self.view, "Empty Basket", "No shares selected to buy.")
            return

        user_id = "1"
        if hasattr(self.app, "current_user") and self.app.current_user:
            user_id = self.app.current_user.id

        # --- Step 1: load saved cards via the model ---
        trade_model = TradeModel()
        saved_cards = []
        try:
            # Use the model, which knows how to talk to the API Client
            response = trade_model.get_saved_cards(user_id)
            if response.get("status") == "success":
                saved_cards = response.get("cards", [])
        except Exception as e:
            print(f"⚠️ Failed to fetch saved cards: {e}")

        # --- Step 2: open the checkout/verification dialog ---
        print("💳 Opening TradeView for checkout...")
        checkout_dialog = BasketCheckoutDialog(self.view, total_amount=grand_total)

        if saved_cards:
            checkout_dialog.trade_view.load_saved_cards(saved_cards)

        if checkout_dialog.exec():
            # The user passed validation and clicked CONFIRM
            card_to_use = checkout_dialog.card_data
            save_card_flag = card_to_use.get("save_card", False)
        else:
            print("❌ Checkout cancelled by user.")
            return

        # --- Step 3: execute buys against the server with the real data ---
        success_count = 0
        for trade in trades_to_execute:
            print(
                f"🚀 Sending Buy Order via Model: {trade['amount']} of {trade['symbol']}..."
            )
            real_sector = trade_model.get_stock_sector(trade["symbol"])

            payload = {
                "symbol": trade["symbol"],
                "amount": trade["amount"],
                "price": trade["price"],
                "user_id": user_id,
                "sector": real_sector,
                "save_card": save_card_flag,
                "card_holder": card_to_use.get("card_holder", ""),
                "card_number": card_to_use.get("card_number", ""),
                "expiration": card_to_use.get("expiration", ""),
                "cvv": card_to_use.get("cvv", ""),
            }

            try:
                # Correct routing in the architecture
                response = trade_model.send_trade_request("buy", payload)

                if response.status_code in [200, 201]:
                    print(f"✅ Successfully bought {trade['symbol']}")
                    success_count += 1
                    save_card_flag = False
                else:
                    err = response.json().get("detail", "Unknown error")
                    print(f"❌ Server Error for {trade['symbol']}: {err}")

            except Exception as e:
                print(f"❌ Execution error: {e}")

            # --- Step 4: finish and refresh dashboard ---
        if success_count > 0:
            QMessageBox.information(
                self.view,
                "Success",
                f"Successfully executed {success_count} trades! 🚀",
            )
            self.view.accept()

            try:
                if hasattr(self.app, "portfolio_module"):
                    self.app.portfolio_module.load_watchlist()
            except Exception as e:
                pass
        else:
            QMessageBox.warning(self.view, "Failed", "Could not execute trades.")
