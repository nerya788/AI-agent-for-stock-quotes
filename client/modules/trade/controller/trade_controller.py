from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from client.modules.trade.view.trade_view import TradeView
from client.modules.trade.models.trade_model import TradeModel  # Import the new model


class TradeController(QDialog):
    def __init__(self, parent=None, app_controller=None):
        super().__init__(parent)
        self.app = app_controller
        self.model = TradeModel()  # Create model

        self.setModal(True)
        self.trade_view = TradeView()

        layout = QVBoxLayout()
        layout.addWidget(self.trade_view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.trade_view.on_trade_clicked.connect(self.execute_trade)
        self.trade_view.on_cancel_clicked.connect(self.reject)

    def _load_user_context(self):
        """Load saved cards from the model."""
        if self.app and self.app.current_user:
            user_id = self.app.current_user.id
            response = self.model.get_saved_cards(user_id)

            if response.get("status") == "success":
                cards = response.get("cards", [])
                self.trade_view.load_saved_cards(cards)

    def open_purchase_window(self, symbol, price, initial_amount=1):
        self.setWindowTitle(f"Buy {symbol}")
        self.trade_view.set_mode("buy")
        self.trade_view.set_stock_data(symbol, price)
        self.trade_view.amount_spin.setValue(initial_amount)
        self._load_user_context()
        self.exec()

    def open_sale_window(
        self,
        symbol,
        current_price,
        available_qty,
        buy_price,
        event_id,
        initial_amount=1,
    ):
        self.setWindowTitle(f"Sell {symbol}")
        self.trade_view.set_mode("sell")
        self.trade_view.set_stock_data(
            symbol, current_price, available_qty, buy_price, event_id
        )
        self.trade_view.amount_spin.setValue(initial_amount)
        self._load_user_context()
        self.exec()

    def execute_trade(self, data):
        # 1. User authentication
        if not self.app or not self.app.current_user:
            QMessageBox.warning(self, "Error", "User not logged in")
            return
        data["user_id"] = self.app.current_user.id

        # 2. Validate via the model (MVC!)
        errors = self.model.validate_purchase_input(data)
        if errors:
            QMessageBox.warning(self, "Input Error", "\n".join(errors))
            return

        # 3. Send to server via the model
        real_sector = self.model.get_stock_sector(data["symbol"])
        data["sector"] = real_sector
        mode = self.trade_view.trade_mode
        try:
            print(f"🚀 Sending {mode} request via Model...")
            # --- DEBUG TRAP #1 (Client) ---
            print("\n🔍 --- DEBUG CLIENT START ---")
            print(
                f"1. User ID in App: {self.app.current_user.id if self.app.current_user else 'NONE'}"
            )
            print(f"2. Data to send: {data}")
            print(f"3. User ID inside Data dict: {data.get('user_id')}")
            print("🔍 --- DEBUG CLIENT END ---\n")
            # ------------------------------
            response = self.model.send_trade_request(mode, data)

            if response.status_code == 200:
                self._handle_success(data, mode)
            else:
                err = response.json().get("detail", "Unknown error")
                QMessageBox.critical(self, "Failed", f"Server Error: {err}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {e}")

    def _handle_success(self, data, mode):
        print(f"✅ {mode} successful")

        if mode == "buy":
            # --- Fetch real sector via the model ---
            real_sector = self.model.get_stock_sector(data["symbol"])

            # Update dashboard
            if self.app and hasattr(self.app, "portfolio_module"):
                stock_entry = {
                    "symbol": data["symbol"],
                    "price": float(
                        data.get("price", 0)
                    ),  # Previously this was current_price
                    "sector": real_sector,  # The real sector!
                    "amount": int(data.get("amount", 0)),
                }
                self.app.portfolio_module.add_stock_entry(stock_entry)

        # General refresh
        if self.app and hasattr(self.app, "portfolio_module"):
            self.app.portfolio_module.load_watchlist()

        QMessageBox.information(
            self, "Success", f"Transaction ({mode}) completed successfully!"
        )
        self.accept()
