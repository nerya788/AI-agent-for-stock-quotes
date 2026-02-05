from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QStackedWidget
from client.modules.trade.view.trade_view import TradeView
import requests

class TradeController(QDialog):
    def __init__(self, parent=None, app_controller=None):
        super().__init__(parent)
        self.app = app_controller
        self.setModal(True)
        self.setWindowTitle("Trade Window")
        
        self.trade_view = TradeView()

        layout = QVBoxLayout()
        layout.addWidget(self.trade_view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setup_connections()

    def setup_connections(self):
        self.trade_view.on_trade_clicked.connect(self.execute_trade)
        self.trade_view.on_cancel_clicked.connect(self.reject)

    def _load_saved_cards(self):
        if self.app and hasattr(self.app, 'current_user') and self.app.current_user:
            try:
                user_id = self.app.current_user.id
                print(f"🔍 Loading saved cards for user: {user_id}")
                
                cards_response = self.app.api.get_saved_cards(user_id)
                print(f"📥 Cards Response: {cards_response}")
                
                if cards_response.get("status") == "success":
                    cards = cards_response.get("cards", [])
                    print(f"✅ Loaded {len(cards)} saved cards")
                    self.trade_view.load_saved_cards(cards)
                else:
                    print(f"⚠️ No cards found or error: {cards_response}")
                    self.trade_view.load_saved_cards([])
            except Exception as e:
                print(f"❌ Exception loading saved cards: {e}")
                import traceback
                traceback.print_exc()
                self.trade_view.load_saved_cards([])
        else:
            print("⚠️ No current user or app_controller not available")
            self.trade_view.load_saved_cards([])

    def open_purchase_window(self, symbol, price):
        self.setWindowTitle("Trade Window - Buy")
        self.trade_view.set_mode("buy")
        self.trade_view.set_stock_data(symbol, price, 0, 0)
        self._load_saved_cards()
        self.exec()

    def open_sale_window(self, symbol, current_price, available_qty, buy_price, event_id):
        """פתיחת חלון מכירה לקנייה ספציפית"""
        self.setWindowTitle("Trade Window - Sell")
        self.trade_view.set_mode("sell")
        self.trade_view.set_stock_data(symbol, current_price, available_qty, buy_price, event_id)
        self._load_saved_cards()
        self.exec()

    def execute_purchase(self, data):
        print(f"🚀 Starting purchase process for {data['symbol']}...")

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
            url = "http://127.0.0.1:8000/trade/buy"
            print(f"📡 Sending POST request to: {url}")
            
            response = requests.post(url, json=data, timeout=5) # הוספתי Timeout
            
            print(f"📥 Server Response Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Purchase successful!")
                QMessageBox.information(self, "Success! 🎉", 
                                      f"Purchase Completed!\nBought {data['amount']} shares of {data['symbol']}.\n\nCheck your Dashboard to see the new stock.")
                
                # הוסף למניות ועדכן דשבורד
                if self.app and hasattr(self.app, 'portfolio_module'):
                    stock_entry = {
                        "symbol": data['symbol'],
                        "price": float(data.get('price', 0)),
                        "sector": "N/A",
                        "change_percent": 0,
                        "amount": int(data.get('amount', 0))
                    }
                    self.app.portfolio_module.add_stock_entry(stock_entry)

                # שמור את האירוע ל-stock_events עם user_id
                if self.app and hasattr(self.app, 'current_user') and self.app.current_user:
                    try:
                        event_url = "http://127.0.0.1:8000/stocks/event"
                        event_data = {
                            "user_id": self.app.current_user.id,
                            "symbol": data['symbol'],
                            "event_type": "STOCK_PURCHASED",
                            "payload": {
                                "amount": int(data.get('amount', 0)),
                                "price": float(data.get('price', 0)),
                                "total": float(data.get('price', 0)) * int(data.get('amount', 0))
                            }
                        }
                        event_response = requests.post(event_url, json=event_data, timeout=5)
                        if event_response.status_code == 200:
                            print(f"✅ Stock event recorded for user {self.app.current_user.id}")
                            if self.app and hasattr(self.app, 'portfolio_module'):
                                self.app.portfolio_module.load_watchlist()
                        else:
                            print(f"⚠️ Warning: Could not record stock event: {event_response.text}")
                    except Exception as e:
                        print(f"⚠️ Warning: Error recording stock event: {e}")

                self.accept() # סוגר את החלון בהצלחה ומחזיר שליטה
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

    def execute_trade(self, data):
        """ביצוע קנייה או מכירה בהתאם למצב"""
        if self.trade_view.trade_mode == "buy":
            self.execute_purchase(data)
        else:
            self.execute_sale(data)

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