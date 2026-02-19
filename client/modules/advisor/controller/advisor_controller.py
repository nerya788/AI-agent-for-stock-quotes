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
        # חיבור לסיגנל של הצ'אט
        self.view.send_message.connect(self.handle_user_message)

    def handle_user_message(self, text):
        """פונקציה שנקראת כשהמשתמש שולח הודעה בצ'אט"""
        # בדיקה שהמשתמש מחובר
        if not self.app.current_user:
            self.view.add_message("System", "Please log in first.", Qt.AlignLeft)
            return

        user_id = self.app.current_user.id
        
        # הפעלת התהליכון ברקע
        self.worker = WorkerThread(self._chat_task, text, user_id)
        self.worker.finished.connect(self.on_ai_response)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    # --- פונקציית רקע (Worker) ---
    def _chat_task(self, text, user_id):
        """שולח את ההודעה לשרת ומחזיר אובייקט AdvisorModel"""
        # כתובת ה-API של הסוכן
        url = "http://127.0.0.1:8000/stocks/agent/chat"
        
        try:
            # שליחת בקשה לשרת
            response = requests.post(
                url, 
                json={"message": text, "user_id": user_id}, 
                timeout=120
            )
            
            if response.status_code == 200:
                return AdvisorModel.from_json(response.json())
            else:
                raise Exception(f"Server returned {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise Exception("The AI is taking too long to think. Please try again.")
        except Exception as e:
            raise Exception(f"Communication Error: {str(e)}")

    # --- הנדלר לתשובה (המוח של הקונטרולר) ---
    def on_ai_response(self, advisor_model: AdvisorModel):
        """מקבל את המודל המעובד ומחליט מה לעשות ב-GUI"""
        
        # 1. תמיד מציגים את הודעת הטקסט של ה-AI
        self.view.add_message("AI", advisor_model.message, Qt.AlignLeft)

        # 2. בדיקה: האם הסוכן ביקש לפתוח טופס?
        if advisor_model.is_form():
            print("🚀 Agent requested to open Investment Form")
            self.app.navigate_to_portfolio() # מעבר למסך התיק
            self.app.portfolio_module.show_investment() # פתיחת הטופס

        # 3. בדיקה: האם הסוכן מציע עסקה?
        elif advisor_model.is_trade():
            print("💰 Agent proposes a trade")
            self._handle_trade_confirmation(advisor_model.trade_payload)

    def _handle_trade_confirmation(self, payload):
        """לוגיקה חכמה לפתיחת חלון קנייה או מכירה"""
        if not payload: return

        symbol = payload.get('symbol')
        amount = payload.get('amount')
        price = payload.get('price')
        side = payload.get('side', 'buy') # ברירת מחדל לקנייה

        # ניסוח ההודעה למשתמש
        action_verb = "Buying" if side == "buy" else "Selling"

        reply = QMessageBox.question(
            self.view, 
            "AI Trade Assistant", 
            f"The Agent suggests {action_verb}:\n\n"
            f"📈 Stock: {symbol}\n"
            f"🔢 Amount: {amount}\n"
            f"💲 Est. Price: ${price}\n\n"
            f"Do you want to proceed to the order window?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # בדיקת תקינות לפני גישה למודול
            if not hasattr(self.app, 'portfolio_module') or not hasattr(self.app.portfolio_module, 'trade_controller'):
                self.view.add_message("System", "Error: Portfolio module not initialized.", Qt.AlignLeft)
                return

            portfolio = self.app.portfolio_module
            
            if side == "sell":
                # --- לוגיקה למכירה: חיפוש המניה בתיק ---
                found_holding = None
                
                # אנחנו עוברים על המניות בתיק כדי למצוא את המניה המבוקשת
                for eid, data in portfolio.stocks_data.items():
                    if data['symbol'] == symbol:
                        found_holding = data
                        found_holding['event_id'] = eid # שומרים את ה-ID
                        break
                
                if found_holding:
                    # פתיחת חלון המכירה עם הנתונים האמיתיים מהתיק
                    portfolio.trade_controller.open_sale_window(
                        symbol=found_holding['symbol'],
                        current_price=price,
                        available_qty=found_holding['amount'],
                        buy_price=found_holding['buy_price'],
                        event_id=found_holding['event_id'],
                        initial_amount=amount
                    )
                else:
                    QMessageBox.warning(self.view, "Error", f"You don't own any shares of {symbol} to sell.")

            else:
                # --- לוגיקה לקנייה (רגיל) ---
                portfolio.trade_controller.open_purchase_window(symbol, price, initial_amount=amount)

    def on_error(self, error_msg):
        self.view.add_message("System", f"Error: {error_msg}", Qt.AlignLeft)