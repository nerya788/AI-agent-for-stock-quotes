from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from client.modules.trade.view.purchase_view import PurchaseView
import requests

class TradeController(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Trade Window")
        
        self.view = PurchaseView()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setup_connections()

    def setup_connections(self):
        self.view.on_buy_clicked.connect(self.execute_purchase)
        self.view.on_cancel_clicked.connect(self.reject) # משתמש ב-reject של הדיאלוג

    def open_purchase_window(self, symbol, price):
        self.view.set_stock_data(symbol, price)
        self.exec()

    def execute_purchase(self, data):
        print(f"🚀 Starting purchase process for {data['symbol']}...")

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