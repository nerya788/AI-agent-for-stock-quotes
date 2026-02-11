from PySide6.QtWidgets import QMessageBox, QApplication, QLabel
from PySide6.QtCore import QObject  # נדרש לעיתים לסיגנלים
from client.modules.explorer.view.explorer_view import ExplorerView
from client.core.api_client import APIClient
from client.core.worker_thread import WorkerThread  # <--- הוספנו את המנוע!
import requests


class ExplorerController:
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = ExplorerView()
        self.api = APIClient()
        self.current_symbol = None
        self.current_news_lang = "en"

        # משתנים לשמירת התהליכונים בזיכרון
        self.search_worker = None
        self.ai_worker = None
        self.news_worker = None
        self.browse_worker = None

        self.setup_connections()

    def setup_connections(self):
        self.view.search_btn.clicked.connect(self.handle_search)
        self.view.ai_btn.clicked.connect(self.handle_ai)
        self.view.save_btn.clicked.connect(self.handle_save)
        self.view.back_btn.clicked.connect(self.handle_back)
        self.view.trade_btn.clicked.connect(self.open_trade_window)
        self.view.browse_btn.clicked.connect(self.show_popular_stocks)
        self.view.translate_btn.clicked.connect(self.handle_translate_news)

    # --- פונקציות רקע (העבודה השחורה) ---

    def _search_task(self, symbol):
        """מביא את כל הנתונים במכה אחת ברקע"""
        # 1. מחיר
        quote = self.api.get_live_quote(symbol)
        # 2. היסטוריה
        history = self.api.get_stock_history(symbol)
        # 3. חדשות (באנגלית כברירת מחדל)
        news_data = self.api.get_stock_news(symbol, lang="en")

        return {"quote": quote, "history": history, "news": news_data}

    def _ai_task(self, symbol):
        """פונה ל-AI ברקע"""
        response = self.api.get_ai_analysis(symbol)
        return response.get('analysis', 'No analysis available.')

    def _news_task(self, symbol, lang):
        """מביא רק חדשות (לתרגום)"""
        return self.api.get_stock_news(symbol, lang=lang)

    def _browse_task(self):
        """מביא רשימת מניות פופולריות ברקע"""
        return self.api.get_popular_stocks()

    # --- הנדלרים (מטפלים בלחיצות) ---

    def handle_search(self):
        symbol = self.view.symbol_input.text().upper().strip()
        if not symbol: return

        self.current_symbol = symbol
        self.current_news_lang = "en"

        # עדכון UI לפני יציאה לעבודה
        self.view.info_label.setText("Fetching data... 🚀")
        self.view.search_btn.setEnabled(False)
        self.view.ai_btn.setEnabled(False)

        # הפעלת התהליכון
        self.search_worker = WorkerThread(self._search_task, symbol)
        self.search_worker.finished.connect(self.on_search_ready)
        self.search_worker.error.connect(self.on_error)
        self.search_worker.start()

    def on_search_ready(self, data):
        """נקרא כשהמידע חוזר מהשרת"""
        self.view.search_btn.setEnabled(True)
        quote = data.get("quote")

        if quote:
            self.view.info_label.setText(f"Stock: {quote['symbol']} | Price: ${quote['price']}")
            self.view.ai_btn.setEnabled(True)
            self.view.save_btn.setEnabled(True)
            self.view.trade_btn.setEnabled(True)
            self.view.translate_btn.setEnabled(True)

            # הצגת גרף
            history = data.get("history")
            if history:
                prices = history.get('prices', [])
                formatted_data = [{'price': p} for p in prices]
                self.view.plot_chart(quote['symbol'], formatted_data)

            # הצגת חדשות
            news_res = data.get("news", {})
            news_items = news_res.get("news", []) if isinstance(news_res, dict) else []
            self.view.show_news_items(quote['symbol'], news_items)

        else:
            self.view.info_label.setText("Stock not found.")
            self.view.trade_btn.setEnabled(False)

    def handle_ai(self):
        symbol = self.view.symbol_input.text().upper().strip()
        self.view.ai_result.setVisible(True)
        self.view.ai_result.setText("AI is thinking... 🤖 (UI is active!)")
        self.view.ai_btn.setEnabled(False)

        # הפעלת Worker ל-AI
        self.ai_worker = WorkerThread(self._ai_task, symbol)
        self.ai_worker.finished.connect(self.on_ai_ready)
        self.ai_worker.error.connect(self.on_error)
        self.ai_worker.start()

    def on_ai_ready(self, analysis):
        self.view.ai_btn.setEnabled(True)
        self.view.ai_result.setText(f"💡 AI Analysis:\n{analysis}")

    def handle_translate_news(self):
        """תרגום חדשות ברקע"""
        if not self.current_symbol: return

        # Toggle שפה
        if self.current_news_lang == "en":
            self.current_news_lang = "he"
            self.view.translate_btn.setText("הצג באנגלית 🌐")
        else:
            self.current_news_lang = "en"
            self.view.translate_btn.setText("תרגם לעברית 🇮🇱")

        self.view.set_news_loading(self.current_symbol)

        # Worker לחדשות בלבד
        self.news_worker = WorkerThread(self._news_task, self.current_symbol, self.current_news_lang)
        self.news_worker.finished.connect(self.on_news_ready)
        self.news_worker.start()

    def on_news_ready(self, result):
        news_items = result.get("news", []) if isinstance(result, dict) else []
        self.view.show_news_items(self.current_symbol, news_items)

    def show_popular_stocks(self):
        """טעינת מניות פופולריות ברקע"""
        self.view.info_label.setText("⏳ Loading popular stocks...")
        self.view.browse_btn.setEnabled(False)

        self.browse_worker = WorkerThread(self._browse_task)
        self.browse_worker.finished.connect(self.on_popular_stocks_ready)
        self.browse_worker.error.connect(self.on_error)
        self.browse_worker.start()

    def on_popular_stocks_ready(self, result):
        self.view.browse_btn.setEnabled(True)
        self.view.info_label.setText("Select a stock from the list")

        stocks = result.get('stocks', []) if isinstance(result, dict) else []
        if not stocks:
            QMessageBox.warning(self.view, "No Results", "No popular stocks found.")
            return

        # --- יצירת החלון (קוד מקורי שלך) ---
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget,
                                       QTableWidgetItem, QPushButton, QHeaderView)

        dialog = QDialog(self.view)
        dialog.setWindowTitle("Browse Popular Stocks 📊")
        dialog.resize(1000, 600)
        dialog.setStyleSheet("background-color: #1e1e2e; color: white;")

        layout = QVBoxLayout(dialog)

        header = QLabel("Top Stocks from S&P 500")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa;")
        layout.addWidget(header)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Symbol", "Name", "Price", "Action"])
        table.setRowCount(len(stocks))
        table.setStyleSheet("QTableWidget { background-color: #313244; color: white; }")

        for row, stock in enumerate(stocks):
            symbol = stock.get('symbol', 'N/A')
            table.setItem(row, 0, QTableWidgetItem(symbol))
            table.setItem(row, 1, QTableWidgetItem(stock.get('name', 'N/A')[:40]))
            table.setItem(row, 2, QTableWidgetItem(f"${stock.get('price', 0)}"))

            btn = QPushButton("View")
            btn.setStyleSheet("background-color: #89b4fa; color: #1e1e2e;")
            btn.clicked.connect(lambda ch, s=symbol: self.search_stock_from_browse(s, dialog))
            table.setCellWidget(row, 3, btn)

        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def search_stock_from_browse(self, symbol, dialog):
        self.view.symbol_input.setText(symbol)
        dialog.close()
        self.handle_search()

    def handle_save(self):
        symbol = self.view.symbol_input.text().upper().strip()
        try:
            resp = requests.post(f"http://127.0.0.1:8000/stocks/watchlist/auto?symbol={symbol}")
            if resp.status_code == 200:
                QMessageBox.information(self.view, "Success", f"Saved {symbol} to watchlist!")
            else:
                QMessageBox.warning(self.view, "Error", "Failed to save stock.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Connection error: {e}")

    def handle_back(self):
        if hasattr(self.app, 'navigate_to_portfolio'):
            self.app.navigate_to_portfolio()

    def open_trade_window(self):
        # לוגיקה מקורית (ללא שינוי)
        symbol = self.view.symbol_input.text().upper()
        price_text = self.view.info_label.text().split("$")[-1]
        try:
            price = float(price_text)
            from client.modules.trade.controller.trade_controller import TradeController
            trade_dialog = TradeController(self.view, self.app)
            trade_dialog.open_purchase_window(symbol, price)
        except ValueError:
            print("Error parsing price")

    def on_error(self, error_msg):
        self.view.search_btn.setEnabled(True)
        self.view.ai_btn.setEnabled(True)
        self.view.browse_btn.setEnabled(True)
        self.view.info_label.setText(f"Error: {error_msg}")