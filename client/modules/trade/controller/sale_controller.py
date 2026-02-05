from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from client.modules.trade.view.sale_view import SaleView
import requests

class SaleController(QDialog):
    def __init__(self, parent=None, app_controller=None):
        super().__init__(parent)
        self.app = app_controller
        self.setModal(True)
        self.setWindowTitle("Trade Window - Sell")
        
        self.view = SaleView()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setup_connections()

    def setup_connections(self):
        self.view.on_sell_clicked.connect(self.execute_sale)
        self.view.on_cancel_clicked.connect(self.reject)

    def open_sale_window(self, symbol, current_price, available_qty, buy_price):
        """פתיחת חלון המכירה"""
        self.view.set_stock_data(symbol, current_price, available_qty, buy_price)
        
        # טען כרטיסים שמורים עבור המשתמש הנוכחי
        if self.app and hasattr(self.app, 'current_user') and self.app.current_user:
            try:
                user_id = self.app.current_user.id
                print(f"🔍 Loading saved cards for user: {user_id}")
                
                cards_response = self.app.api.get_saved_cards(user_id)
                print(f"📥 Cards Response: {cards_response}")
                
                if cards_response.get("status") == "success":
                    cards = cards_response.get("cards", [])
                    print(f"✅ Loaded {len(cards)} saved cards")
                    self.view.load_saved_cards(cards)
                else:
                    print(f"⚠️ No cards found or error: {cards_response}")
                    self.view.load_saved_cards([])
            except Exception as e:
                print(f"❌ Exception loading saved cards: {e}")
                import traceback
                traceback.print_exc()
                self.view.load_saved_cards([])
        else:
            print("⚠️ No current user or app_controller not available")
            self.view.load_saved_cards([])
        
        self.exec()

    def execute_sale(self, data):
        print(f"🚀 Starting sale process for {data['symbol']}...")

        # הוסף user_id מ-app_controller
        if self.app and hasattr(self.app, 'current_user') and self.app.current_user:
            data['user_id'] = self.app.current_user.id
        else:
            QMessageBox.warning(self, "Authentication Error", "User not logged in.")
            return

        # ולידציה בסיסית לפני שליחה
        if len(data['card_number']) != 16:
            QMessageBox.warning(self, "Invalid Card", "Card number must be exactly 16 digits.")
            return
        if not data['card_holder']:
            QMessageBox.warning(self, "Missing Name", "Please enter card holder name.")
            return

        try:
            # כתובת ה-API שלך
            url = "http://127.0.0.1:8000/trade/sell"
            print(f"📡 Sending POST request to: {url}")
            
            response = requests.post(url, json=data, timeout=5)
            
            print(f"📥 Server Response Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Sale successful!")
                
                income = data['amount'] * data['current_price']
                pnl = (data['current_price'] - data['buy_price']) * data['amount']
                
                message = f"Sale Completed!\nSold {data['amount']} shares of {data['symbol']}.\n"
                message += f"Income: ${income:,.2f}\n"
                message += f"Profit/Loss: ${pnl:,.2f}\n\n"
                message += f"Check your Dashboard to see the updated portfolio."
                
                QMessageBox.information(self, "Success! 🎉", message)
                
                # עדכן את הדשבורד עם הנתונים החדשים
                if self.app and hasattr(self.app, 'portfolio_module'):
                    print("🔄 Refreshing dashboard after sale...")
                    self.app.portfolio_module.load_watchlist()
                    print("✅ Dashboard refreshed!")

                self.accept()
            else:
                try:
                    error_detail = response.json().get('detail', response.text)
                except:
                    error_detail = response.text
                
                print(f"❌ Server Error: {error_detail}")
                QMessageBox.critical(self, "Transaction Failed", f"Server Error:\n{error_detail}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Server is down or unreachable.")
            QMessageBox.critical(self, "Network Error", "Could not connect to the server.\nIs the backend running?")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{e}")
