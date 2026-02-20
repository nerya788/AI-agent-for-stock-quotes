from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import requests

# Import views
from client.modules.portfolio.view.dashboard_view import DashboardView
from client.modules.portfolio.view.investment_view import InvestmentView
from client.modules.trade.controller.trade_controller import TradeController
from client.core.api_client import APIClient
from client.core.worker_thread import WorkerThread  # <--- added the worker engine!
from client.modules.trade.view.basket_view import BasketView
from client.modules.trade.controller.basket_controller import BasketController


# from client.modules.portfolio.view.stock_search_dialog import StockSearchDialog


class PortfolioController(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.api = APIClient()
        self.stocks_data = {}  # Store stock data

        # Worker thread references
        self.watchlist_worker = None
        self.ai_worker = None

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Internal screen management (dashboard <-> investments)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Create screens
        self.dashboard_view = DashboardView()
        self.investment_view = InvestmentView()
        self.trade_controller = TradeController(parent=self, app_controller=self.app)

        self.stack.addWidget(self.dashboard_view)  # Index 0
        self.stack.addWidget(self.investment_view)  # Index 1

        self.setup_connections()

    def setup_connections(self):
        # Switch from dashboard to "AI Advisor"
        self.dashboard_view.ai_consult_btn.clicked.connect(self.open_advisor_chat)
        # Wire the AI button to generate a recommendation
        self.investment_view.submit_btn.clicked.connect(self.handle_ai_recommendation)

        # Back button to AI Advisor
        self.investment_view.back_btn.clicked.connect(self.back_to_advisor)

        # Execute recommendation button (open shopping basket)
        self.investment_view.execute_btn.clicked.connect(self.execute_basket)

        # Wire logout button
        if hasattr(self.dashboard_view, "logout_btn"):
            self.dashboard_view.logout_btn.clicked.connect(self.handle_logout)

        if hasattr(self.dashboard_view, "explorer_btn"):
            self.dashboard_view.explorer_btn.clicked.connect(self.open_explorer)

    def open_advisor_chat(self):
        """Ask the main application to navigate to the chat screen."""
        print("🔀 Switching to AI Chat Module...")
        if hasattr(self.app, "navigate_to_advisor"):
            self.app.navigate_to_advisor()

    def show_investment(self):
        self.stack.setCurrentWidget(self.investment_view)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard_view)
        self.update_user_header()
        self.load_watchlist()

    # --- Background tasks ---

    def _ai_task(self, data):
        """Send the recommendation request to the server in the background."""
        # You can use requests directly or via api_client if you extend it
        response = requests.post(
            f"http://127.0.0.1:8000/stocks/ai-investment-plan",
            json=data,
            timeout=120,
        )
        if response.status_code == 200:
            return response.json().get("recommendation", "No recommendation available")
        else:
            raise Exception(response.json().get("detail", "Unknown server error"))

    def _watchlist_task(self, user_id):
        """Load the portfolio and compute data in the background (the heavy part)."""
        url = f"http://127.0.0.1:8000/stocks/watchlist/{user_id}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json().get("data", [])
        stocks_processed = []

        for item in data:
            symbol = item.get("symbol")
            avg_buy_price = item.get("price", 0)

            # Fetch live price (takes time, so it must run in the background)
            current_market_price = self._get_current_price_sync(symbol)
            if current_market_price == 0:
                current_market_price = avg_buy_price

            # Compute percentage change
            change_percent = 0
            if avg_buy_price > 0:
                change_percent = (
                    (current_market_price - avg_buy_price) / avg_buy_price
                ) * 100

            stocks_processed.append(
                {
                    "event_id": item.get("id"),
                    "symbol": symbol,
                    "price": current_market_price,
                    "buy_price": avg_buy_price,
                    "sector": item.get("sector", "Unknown"),
                    "change_percent": round(change_percent, 2),
                    "amount": item.get("amount", 0),
                }
            )

        return stocks_processed

    def _get_current_price_sync(self, symbol):
        """Synchronous helper function for use inside the worker thread."""
        try:
            quote = self.api.get_live_quote(symbol)
            if quote and "price" in quote:
                return quote.get("price")
            return 0
        except:
            return 0

    # --- UI handlers ---

    def handle_ai_recommendation(self):
        """Handle clicking the green button (without freezing the UI)."""
        # Collect input data
        amount = self.investment_view.amount_input.text()
        if not amount:
            QMessageBox.warning(
                self.investment_view, "Error", "Please enter investment amount"
            )
            return

        data = {
            "amount": amount,
            "sector": self.investment_view.sector_combo.currentText(),
            "risk": self.investment_view.risk_combo.currentText(),
            "availability": self.investment_view.availability_combo.currentText(),
            "location": self.investment_view.location_combo.currentText(),
        }

        # Update UI
        self.investment_view.submit_btn.setEnabled(False)
        self.investment_view.submit_btn.setText("⏳ AI is thinking...")
        self.investment_view.ai_response_box.setText(
            "🔄 Processing your plan... (You can move the window!)"
        )

        # Start worker
        self.ai_worker = WorkerThread(self._ai_task, data)
        self.ai_worker.finished.connect(self.on_ai_success)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_ai_success(self, recommendation):
        # Safe check: hide the loading indicator only if it exists in the UI
        if hasattr(self.investment_view, "loading_label"):
            self.investment_view.loading_label.hide()

        if isinstance(recommendation, dict):
            display_text = recommendation.get("plan_text", "Could not load plan text.")
            self.investment_view.ai_response_box.setText(display_text)
            self.current_basket = recommendation.get("basket", [])

            if self.current_basket:
                self.investment_view.execute_btn.show()
            else:
                self.investment_view.execute_btn.hide()  # Hide if the basket is empty due to an AI error

        else:
            self.investment_view.ai_response_box.setText(str(recommendation))
            self.current_basket = []
            self.investment_view.execute_btn.hide()

        # --- Critical fix: call submit_btn instead of generate_btn ---
        self.investment_view.submit_btn.setEnabled(True)
        self.investment_view.submit_btn.setText("Generate AI Recommendation 🚀")

    def on_ai_error(self, error_msg):
        self.investment_view.submit_btn.setEnabled(True)
        self.investment_view.submit_btn.setText("Generate AI Recommendation 🚀")
        self.investment_view.ai_response_box.setText(f"❌ Error: {error_msg}")
        print(f"[DEBUG] on_ai_error called: {error_msg}")

    def on_buy_error(self, error_msg):
        print(f"[DEBUG] on_buy_error called: {error_msg}")
        QMessageBox.critical(self, "Buy Error", str(error_msg))

    def load_watchlist(self):
        """Load the portfolio in the background."""
        if not getattr(self.app, "current_user", None):
            return

        print("📊 Loading Portfolio in background...")
        user_id = self.app.current_user.id

        # If a previous worker is running, stop it first
        if hasattr(self, "watchlist_worker") and self.watchlist_worker is not None:
            if self.watchlist_worker.isRunning():
                print("[DEBUG] load_watchlist: Stopping previous watchlist_worker...")
                self.watchlist_worker.quit()
                self.watchlist_worker.wait()

        # Start worker to load the portfolio
        self.watchlist_worker = WorkerThread(self._watchlist_task, user_id)
        self.watchlist_worker.finished.connect(
            self.display_stocks
        )  # When ready -> display
        self.watchlist_worker.start()

    def display_stocks(self, stocks):
        """Display data in the table (runs in the main thread after computation completes)."""
        self.dashboard_view.stock_table.setRowCount(len(stocks))
        self.stocks_data = {}

        for row, stock in enumerate(stocks):
            # ... (your excellent display code) ...
            event_id = stock["event_id"]
            symbol = stock["symbol"]
            current_price = stock["price"]
            change_percent = stock["change_percent"]

            # Save data for selling
            self.stocks_data[event_id] = {
                "symbol": symbol,
                "current_price": current_price,
                "amount": stock["amount"],
                "buy_price": stock["buy_price"],
            }

            # Colors
            if change_percent > 0:
                color = QColor("#a6e3a1")
            elif change_percent < 0:
                color = QColor("#f38ba8")
            else:
                color = QColor("#cdd6f4")

            # Fill the table
            self.dashboard_view.stock_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.dashboard_view.stock_table.setItem(
                row, 1, QTableWidgetItem(f"${stock['buy_price']:.2f}")
            )

            price_item = QTableWidgetItem(f"${current_price:.2f}")
            price_item.setForeground(color)
            self.dashboard_view.stock_table.setItem(row, 2, price_item)

            self.dashboard_view.stock_table.setItem(
                row, 3, QTableWidgetItem(str(int(stock["amount"])))
            )
            self.dashboard_view.stock_table.setItem(
                row, 4, QTableWidgetItem(stock["sector"])
            )

            change_text = f"{change_percent:+.2f}%" if change_percent != 0 else "0.00%"
            change_item = QTableWidgetItem(change_text)
            change_item.setForeground(color)
            self.dashboard_view.stock_table.setItem(row, 5, change_item)

            # ---  Container for action buttons ---
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2) 
            action_layout.setSpacing(5) 

            # buy button
            buy_btn = QPushButton("📈 Buy")
            buy_btn.setStyleSheet("""
                QPushButton { background-color: #a6e3a1; color: #1e1e2e; border-radius: 4px; padding: 4px; border: none; font-weight: bold;}
                QPushButton:hover { background-color: #b5e8b0; }
            """)
            buy_btn.setCursor(Qt.PointingHandCursor)
            buy_btn.clicked.connect(lambda ch, eid=event_id: self.open_buy_dialog(eid))

            # sell button
            sell_btn = QPushButton("📉 Sell")
            sell_btn.setStyleSheet("""
                QPushButton { background-color: #f38ba8; color: #1e1e2e; border-radius: 4px; padding: 4px; border: none; font-weight: bold;}
                QPushButton:hover { background-color: #f5b9d6; }
            """)
            sell_btn.setCursor(Qt.PointingHandCursor)
            sell_btn.clicked.connect(lambda ch, eid=event_id: self.open_sale_dialog(eid))

            # Add buttons to the layout
            action_layout.addWidget(buy_btn)
            action_layout.addWidget(sell_btn)
            self.dashboard_view.stock_table.setCellWidget(row, 6, action_widget)

    def handle_logout(self):
        if hasattr(self.app, "logout"):
            self.app.logout()

    def open_explorer(self):
        if hasattr(self.app, "navigate_to_explorer"):
            self.app.navigate_to_explorer()

    def update_user_header(self):
        try:
            if getattr(self.app, "current_user", None):
                name = self.app.current_user.full_name or self.app.current_user.email
                self.dashboard_view.user_label.setText(f"Welcome, {name}")
        except:
            pass

    def open_sale_dialog(self, event_id):
        if event_id in self.stocks_data:
            s = self.stocks_data[event_id]
            self.trade_controller.open_sale_window(
                s["symbol"], s["current_price"], s["amount"], s["buy_price"], event_id
            )
    
    def open_buy_dialog(self, event_id):
        if event_id in self.stocks_data:
            s = self.stocks_data[event_id]
            # שים לב: תבדוק איך קוראים בדיוק לפונקציית הקנייה ב-trade_controller שלך
            # סביר להניח שזה open_buy_window או משהו דומה שמקבל סימבול ומחיר
            try:
                self.trade_controller.open_buy_window(s["symbol"], s["current_price"])
            except AttributeError:
                print("⚠️ Make sure you have an 'open_buy_window' method in TradeController!")

    # Functions for future additions (Search Dialog)
    def handle_add_stock(self):
        pass

    def add_stock_entry(self, stock):
        self.load_watchlist()

    def back_to_advisor(self):
        """Return to the advisor screen after completing/canceling the investment form."""
        if hasattr(self.app, "navigate_to_advisor"):
            self.app.navigate_to_advisor()

    def execute_basket(self):
        """Open the shopping basket window instead of opening separate trade windows."""
        if not hasattr(self, "current_basket") or not self.current_basket:
            return

        try:
            total_investment = float(self.investment_view.amount_input.text())
        except ValueError:
            total_investment = 1000.0

        print("🛒 Opening Shopping Basket View...")

        # Create the basket window and its controller
        self.basket_view = BasketView()
        self.basket_controller = BasketController(
            app=self.app,
            view=self.basket_view,
            basket_data=self.current_basket,
            total_budget=total_investment,
        )

        # Show the window (exec blocks until the user finishes confirming the basket)
        self.basket_view.exec()
