import webbrowser
from PySide6.QtWidgets import QMessageBox
from client.modules.explorer.view.explorer_view import ExplorerView
from client.core.api_client import APIClient
from client.core.worker_thread import WorkerThread
import requests

class ExplorerController:
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = ExplorerView()
        self.api = APIClient()
        self.current_symbol = None

        self.search_worker = None
        self.ai_worker = None
        self.browse_worker = None

        self.setup_connections()

    def setup_connections(self):
        # חיבורים לכפתורים שנשארו
        self.view.search_btn.clicked.connect(self.handle_search)
        self.view.back_btn.clicked.connect(self.handle_back)
        self.view.trade_btn.clicked.connect(self.open_trade_window)
        self.view.browse_btn.clicked.connect(self.show_popular_stocks)
        
        # חיבור לחיצה כפולה לפתיחת הלינק
        self.view.news_list.itemDoubleClicked.connect(self.open_news_link)

    def _search_task(self, symbol):
        quote = self.api.get_live_quote(symbol)
        history = self.api.get_stock_history(symbol)
        # מביא חדשות רגילות (מדורגות בשרת) ללא פרמטר שפה
        news_data = self.api.get_stock_news(symbol) 
        # בונוס: הפעלת AI אוטומטית (אם תרצה בעתיד) - כרגע לא מופעל
        ai_analysis = self.api.get_ai_analysis(symbol).get('analysis', '')
        return {"quote": quote, "history": history, "news": news_data, "analysis": ai_analysis}

    def _browse_task(self):
        return self.api.get_popular_stocks()

    def handle_search(self):
        symbol = self.view.symbol_input.text().upper().strip()
        if not symbol: return

        self.current_symbol = symbol
        self.view.info_label.setText("Fetching data... 🚀")
        self.view.search_btn.setEnabled(False)
        self.view.ai_result.setVisible(False) # איפוס תוצאת AI קודמת

        self.search_worker = WorkerThread(self._search_task, symbol)
        self.search_worker.finished.connect(self.on_search_ready)
        self.search_worker.error.connect(self.on_error)
        self.search_worker.start()

    def on_search_ready(self, data):
        self.view.search_btn.setEnabled(True)
        quote = data.get("quote")

        if quote:
            self.view.info_label.setText(f"Stock: {quote['symbol']} | Price: ${quote['price']}")
            self.view.trade_btn.setEnabled(True)

            history = data.get("history")
            if history:
                prices = history.get('prices', [])
                formatted_data = [{'price': p} for p in prices]
                self.view.plot_chart(quote['symbol'], formatted_data)

            news_res = data.get("news", {})
            news_items = news_res.get("news", []) if isinstance(news_res, dict) else []
            self.view.show_news_items(quote['symbol'], news_items)
            
            # אם תרצה להציג את הניתוח אוטומטית:
            analysis = data.get("analysis")
            if analysis:
                self.view.ai_result.setVisible(False)
                self.view.ai_result.setText(f"💡 AI Insight: {analysis}")

        else:
            self.view.info_label.setText("Stock not found.")
            self.view.trade_btn.setEnabled(False)

    def show_popular_stocks(self):
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

        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget,
                                       QTableWidgetItem, QPushButton, QHeaderView)

        dialog = QDialog(self.view)
        dialog.setWindowTitle("Browse Popular Stocks 📊")
        dialog.resize(800, 500)
        dialog.setStyleSheet("background-color: #1e1e2e; color: white;")

        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Symbol", "Name", "Price", "Action"])
        table.setRowCount(len(stocks))
        table.setStyleSheet("QTableWidget { background-color: #313244; color: white; }")

        for row, stock in enumerate(stocks):
            symbol = stock.get('symbol', 'N/A')
            table.setItem(row, 0, QTableWidgetItem(symbol))
            table.setItem(row, 1, QTableWidgetItem(stock.get('name', 'N/A')[:30]))
            table.setItem(row, 2, QTableWidgetItem(f"${stock.get('price', 0)}"))

            btn = QPushButton("View")
            btn.setStyleSheet("background-color: #89b4fa; color: #1e1e2e;")
            btn.clicked.connect(lambda ch, s=symbol: self.search_stock_from_browse(s, dialog))
            table.setCellWidget(row, 3, btn)

        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(table)
        dialog.exec()

    def search_stock_from_browse(self, symbol, dialog):
        self.view.symbol_input.setText(symbol)
        dialog.close()
        self.handle_search()

    def handle_back(self):
        if hasattr(self.app, 'navigate_to_portfolio'):
            self.app.navigate_to_portfolio()

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

    def open_news_link(self, item):
        url = item.toolTip()
        if url: webbrowser.open(url)

    def on_error(self, error_msg):
        self.view.search_btn.setEnabled(True)
        self.view.browse_btn.setEnabled(True)
        self.view.info_label.setText(f"Error: {error_msg}")