from PySide6.QtWidgets import QMessageBox, QApplication, QLabel
from client.modules.explorer.view.explorer_view import ExplorerView
from client.core.api_client import APIClient
import requests # נשתמש בזה לשמירה אם חסר ב-API Client

class ExplorerController:
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = ExplorerView() # יצירת ה-View
        self.api = APIClient()
        self.current_symbol = None
        self.current_news_lang = "en"  # 'en' or 'he'
        
        self.setup_connections()

    def setup_connections(self):
        self.view.search_btn.clicked.connect(self.handle_search)
        self.view.ai_btn.clicked.connect(self.handle_ai)
        self.view.save_btn.clicked.connect(self.handle_save)
        self.view.back_btn.clicked.connect(self.handle_back)
        self.view.trade_btn.clicked.connect(self.open_trade_window)
        self.view.browse_btn.clicked.connect(self.show_popular_stocks)
        self.view.translate_btn.clicked.connect(self.handle_translate_news)


    def handle_search(self):
        symbol = self.view.symbol_input.text().upper().strip()
        if not symbol: return

        self.current_symbol = symbol
        self.current_news_lang = "en"

        self.view.info_label.setText("Fetching data...")
        
        # 1. קבלת מחיר
        data = self.api.get_live_quote(symbol)
        if data:
            self.view.info_label.setText(f"Stock: {data['symbol']} | Price: ${data['price']}")
            self.view.ai_btn.setEnabled(True)
            self.view.save_btn.setEnabled(True)
            self.view.trade_btn.setEnabled(True)
            self.view.translate_btn.setEnabled(True)
            
            # 2. קבלת היסטוריה לגרף (רשימת מחירים)
            history = self.api.get_stock_history(symbol)
            if history:
                # אנו צריכים רשימה של אובייקטים עם 'price', נניח שהשרת מחזיר מבנה כזה
                # השרת שלנו מחזיר {'prices': [...], 'dates': [...]}
                # נמיר את זה לפורמט שה-View מצפה לו
                prices = history.get('prices', [])
                formatted_data = [{'price': p} for p in prices] 
                self.view.plot_chart(symbol, formatted_data)
            # 3. טעינת חדשות מדורגות למניה
            self.load_news_for_symbol(symbol, lang=self.current_news_lang)
        else:
            self.view.info_label.setText("Stock not found.")
            self.view.trade_btn.setEnabled(False)
            self.view.translate_btn.setEnabled(False)

    def handle_ai(self):
        symbol = self.view.symbol_input.text().upper().strip()
        self.view.ai_result.setVisible(True)
        self.view.ai_result.setText("AI is thinking... 🤖")
        QApplication.processEvents()

        response = self.api.get_ai_analysis(symbol)
        analysis = response.get('analysis', 'No analysis available.')
        self.view.ai_result.setText(f"💡 AI Analysis:\n{analysis}")

    def handle_save(self):
        symbol = self.view.symbol_input.text().upper().strip()
        # שימוש ב-API Client או requests ישירות אם הפונקציה לא קיימת שם עדיין
        try:
            # אופציה א': אם הוספת ל-APIClient
            # self.api.add_to_watchlist(symbol)
            
            # אופציה ב': חיקוי הלוגיקה המקורית (כדי שיעבוד בטוח)
            resp = requests.post(f"http://127.0.0.1:8000/stocks/watchlist/auto?symbol={symbol}")
            
            if resp.status_code == 200:
                QMessageBox.information(self.view, "Success", f"Saved {symbol} to watchlist!")
            else:
                QMessageBox.warning(self.view, "Error", "Failed to save stock.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Connection error: {e}")

    def load_news_for_symbol(self, symbol: str, lang: str | None = None):
        """טעינת חדשות מהמנוע החדש והצגתן בפאנל החדשות."""
        try:
            self.view.set_news_loading(symbol)
            result = self.api.get_stock_news(symbol, lang=lang)
            news_items = result.get("news", []) if isinstance(result, dict) else []
            self.view.show_news_items(symbol, news_items)
        except Exception as e:
            print(f"❌ Error loading news for {symbol}: {e}")

    def handle_translate_news(self):
        """כפתור תרגום/חזרה לאנגלית לפיד החדשות."""
        if not self.current_symbol:
            return

        # Toggle בין עברית לאנגלית
        if self.current_news_lang == "en":
            self.current_news_lang = "he"
            self.view.translate_btn.setText("הצג באנגלית 🌐")
            self.load_news_for_symbol(self.current_symbol, lang="he")
        else:
            self.current_news_lang = "en"
            self.view.translate_btn.setText("תרגם לעברית 🇮🇱")
            self.load_news_for_symbol(self.current_symbol, lang="en")

    def handle_back(self):
        """חזרה לדשבורד דרך ה-AppController"""
        print("⬅️ Going back to Dashboard...")
        if hasattr(self.app, 'navigate_to_portfolio'):
            self.app.navigate_to_portfolio()
    
    # פונקציה חדשה ב-ExplorerController:
    def open_trade_window(self):
        symbol = self.view.symbol_input.text().upper()
        price_text = self.view.info_label.text().split("$")[-1]
        try:
            price = float(price_text)
            
            from client.modules.trade.controller.trade_controller import TradeController
            
            trade_dialog = TradeController(self.view, self.app)
            trade_dialog.open_purchase_window(symbol, price)
            
        except ValueError:
            print("Error parsing price")

    def show_popular_stocks(self):
        """הצג רשימת חברות פופולריות מ-Finnhub"""
        try:
            self.view.info_label.setText("⏳ Loading popular stocks...")
            QApplication.processEvents()
            
            # קבלת רשימת חברות פופולריות מהשרת דרך APIClient
            result = self.api.get_popular_stocks()
            print(f"📊 Popular stocks result: {result}")
            stocks = result.get('stocks', []) if isinstance(result, dict) else []
            print(f"📊 Stocks list: {stocks}")
            
            if not stocks:
                QMessageBox.warning(self.view, "No Results", "No popular stocks found.")
                return

            # יצירת דיאלוג עם רשימת המניות
            from PySide6.QtWidgets import (QDialog, QVBoxLayout,
                                         QTableWidget, QTableWidgetItem, QPushButton)
            from PySide6.QtCore import Qt
            
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Browse Popular Stocks 📊")
            dialog.setGeometry(100, 100, 1200, 700)
            dialog.setMinimumSize(1000, 600)
            dialog.setStyleSheet("background-color: #1e1e2e; color: white;")
            
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # הוסף לייבל
            header = QLabel("Top Stocks from S&P 500")
            header.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa; margin-bottom: 10px;")
            layout.addWidget(header)
            
            # יצירת טבלה
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Symbol", "Name", "Price", "Action"])
            table.setRowCount(len(stocks))
            table.setStyleSheet("""
                QTableWidget { background-color: #313244; gridline-color: #45475a; }
                QHeaderView::section { background-color: #45475a; color: white; padding: 5px; }
                QTableWidgetItem { padding: 5px; }
            """)
            
            for row, stock in enumerate(stocks):
                symbol_item = QTableWidgetItem(stock.get('symbol', 'N/A'))
                name_item = QTableWidgetItem(stock.get('name', 'N/A')[:40])
                price_value = stock.get('price')
                price_item = QTableWidgetItem(
                    f"${price_value}" if price_value is not None else "N/A"
                )
                
                # כפתור לבחירה
                select_btn = QPushButton("View")
                select_btn.setStyleSheet("background-color: #89b4fa; color: #1e1e2e; padding: 5px;")
                select_btn.clicked.connect(
                    lambda checked, s=stock.get('symbol'): self.search_stock_from_browse(s, dialog)
                )
                
                table.setItem(row, 0, symbol_item)
                table.setItem(row, 1, name_item)
                table.setItem(row, 2, price_item)
                table.setCellWidget(row, 3, select_btn)
            
            table.horizontalHeader().setStretchLastSection(False)
            from PySide6.QtWidgets import QHeaderView
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            layout.addWidget(table, 1)
            
            # כפתור סגירה
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet("background-color: #45475a; color: white; padding: 8px;")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
                
        except Exception as e:
            print(f"❌ Browse stocks error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.view, "Error", f"Error loading stocks: {str(e)}")
            self.view.info_label.setText("Error loading stocks")

    def search_stock_from_browse(self, symbol, dialog):
        """חיפוש מניה שנבחרה מהרשימה ופתיחת הנתונים"""
        self.view.symbol_input.setText(symbol)
        dialog.close()
        self.handle_search()