import requests
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt

from client.modules.advisor.view.advisor_view import AdvisorView
from client.modules.advisor.models.advisor_module import AdvisorModel
from client.core.api_client import APIClient
from client.core.worker_thread import WorkerThread


class AdvisorController:
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = AdvisorView()
        self.api = APIClient()
        self.worker = None

        self.setup_connections()

    def setup_connections(self):
        # Connect to the chat signal
        self.view.send_message.connect(self.handle_user_message)

    def handle_user_message(self, text):
        """Called when the user sends a message in the chat."""
        # Ensure the user is logged in
        if not self.app.current_user:
            self.view.add_message("System", "Please log in first.", Qt.AlignLeft)
            return

        user_id = self.app.current_user.id

        # Run the worker in the background
        self.worker = WorkerThread(self._chat_task, text, user_id)
        self.worker.finished.connect(self.on_ai_response)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    # --- Background function (Worker) ---
    def _chat_task(self, text, user_id):
        """Send the message to the server and return an AdvisorModel object."""
        # Agent API endpoint
        url = "http://127.0.0.1:8000/stocks/agent/chat"

        try:
            # Send request to server
            response = requests.post(
                url, json={"message": text, "user_id": user_id}, timeout=120
            )

            if response.status_code == 200:
                return AdvisorModel.from_json(response.json())
            else:
                raise Exception(f"Server returned {response.status_code}")

        except requests.exceptions.Timeout:
            raise Exception("The AI is taking too long to think. Please try again.")
        except Exception as e:
            raise Exception(f"Communication Error: {str(e)}")

    # --- Response handler (the controller's brain) ---
    def on_ai_response(self, advisor_model: AdvisorModel):
        """Receive the processed model and decide what to do in the GUI."""

        # 1. Always display the AI message text
        self.view.add_message("AI", advisor_model.message, Qt.AlignLeft)

        # 2. Check: did the agent request opening a form?
        if advisor_model.is_form():
            print("🚀 Agent requested to open Investment Form")
            self.app.navigate_to_portfolio()  # Navigate to portfolio screen
            self.app.portfolio_module.show_investment()  # Open the form

        # 3. Check: did the agent propose a trade?
        elif advisor_model.is_trade():
            print("💰 Agent proposes a trade")
            self._handle_trade_confirmation(advisor_model.trade_payload)

    def _handle_trade_confirmation(self, payload):
        """Smart logic for opening a buy or sell window."""
        if not payload:
            return

        symbol = payload.get("symbol")
        amount = payload.get("amount")
        price = payload.get("price")
        side = payload.get("side", "buy")  # Default to buy

        # Build the user-facing message
        action_verb = "Buying" if side == "buy" else "Selling"

        reply = QMessageBox.question(
            self.view,
            "AI Trade Assistant",
            f"The Agent suggests {action_verb}:\n\n"
            f"📈 Stock: {symbol}\n"
            f"🔢 Amount: {amount}\n"
            f"💲 Est. Price: ${price}\n\n"
            f"Do you want to proceed to the order window?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Validate module access before using it
            if not hasattr(self.app, "portfolio_module") or not hasattr(
                self.app.portfolio_module, "trade_controller"
            ):
                self.view.add_message(
                    "System", "Error: Portfolio module not initialized.", Qt.AlignLeft
                )
                return

            portfolio = self.app.portfolio_module

            if side == "sell":
                # --- Sell logic: find the stock in the portfolio ---
                found_holding = None

                # Iterate holdings to find the requested symbol
                for eid, data in portfolio.stocks_data.items():
                    if data["symbol"] == symbol:
                        found_holding = data
                        found_holding["event_id"] = eid  # Save the ID
                        break

                if found_holding:
                    # Open the sell window with real portfolio data
                    portfolio.trade_controller.open_sale_window(
                        symbol=found_holding["symbol"],
                        current_price=price,
                        available_qty=found_holding["amount"],
                        buy_price=found_holding["buy_price"],
                        event_id=found_holding["event_id"],
                        initial_amount=amount,
                    )
                else:
                    QMessageBox.warning(
                        self.view,
                        "Error",
                        f"You don't own any shares of {symbol} to sell.",
                    )

            else:
                # --- Buy logic (standard) ---
                portfolio.trade_controller.open_purchase_window(
                    symbol, price, initial_amount=amount
                )

    def on_error(self, error_msg):
        self.view.add_message("System", f"Error: {error_msg}", Qt.AlignLeft)

    def setup_connections(self):
        # Connect to the chat signal
        self.view.send_message.connect(self.handle_user_message)
        # Added: connect the back button
        self.view.back_btn.clicked.connect(self.go_back_to_dashboard)

    def go_back_to_dashboard(self):
        """Navigate back to the dashboard."""
        if hasattr(self.app, "navigate_to_portfolio"):
            self.app.navigate_to_portfolio()
