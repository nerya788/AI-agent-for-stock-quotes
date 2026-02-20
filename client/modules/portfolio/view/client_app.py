import sys
import requests
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtGui import QPainter
from datetime import datetime

# Local server URL
SERVER_URL = "http://127.0.0.1:8000"


class StockClientApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("מערכת ניהול מניות חכמה - פרויקט גמר")
        self.setGeometry(100, 100, 900, 700)

        # --- Global look & feel ---
        self.setStyleSheet(
            """
            QMainWindow { background-color: #f5f5f5; }
            QLabel { font-size: 14px; color: #333; }
            QLineEdit { padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 5px; }
            QPushButton { padding: 10px; font-size: 14px; border-radius: 5px; font-weight: bold; }
        """
        )

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # --- Header ---
        self.header = QLabel("מערכת סוכן פיננסי (AI Agent)")
        self.header.setStyleSheet(
            "font-size: 24px; color: #1565C0; font-weight: bold; margin-bottom: 10px;"
        )
        self.header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header)

        # --- Search row ---
        search_layout = QHBoxLayout()
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText(
            "הכנס סימול מניה (למשל: NVDA, TSLA, GOOGL)"
        )
        self.symbol_input.setAlignment(Qt.AlignCenter)

        self.search_btn = QPushButton("חפש ונתח 🔍")
        self.search_btn.setStyleSheet("background-color: #1976D2; color: white;")
        self.search_btn.clicked.connect(self.fetch_all_data)

        search_layout.addWidget(self.symbol_input)
        search_layout.addWidget(self.search_btn)
        self.layout.addLayout(search_layout)

        # --- Data display ---
        self.info_label = QLabel("המתנה לנתונים...")
        self.info_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 15px; color: #444;"
        )
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        # --- Chart area (QtCharts) ---
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(
            QPainter.Antialiasing
        )  # Enable anti-aliasing for chart lines
        self.chart_view.setMinimumHeight(400)
        self.layout.addWidget(self.chart_view)

        # --- Actions area (AI and save) ---
        actions_layout = QHBoxLayout()

        self.ai_btn = QPushButton("🤖 התייעץ עם ה-AI")
        self.ai_btn.setStyleSheet("background-color: #7B1FA2; color: white;")
        self.ai_btn.clicked.connect(self.ask_ai_agent)
        self.ai_btn.setEnabled(False)  # Disabled until a stock is loaded

        self.save_btn = QPushButton("☁️ שמור למאגר")
        self.save_btn.setStyleSheet("background-color: #388E3C; color: white;")
        self.save_btn.clicked.connect(self.save_to_cloud)
        self.save_btn.setEnabled(False)

        actions_layout.addWidget(self.ai_btn)
        actions_layout.addWidget(self.save_btn)
        self.layout.addLayout(actions_layout)

        # --- AI result ---
        self.ai_result = QLabel("")
        self.ai_result.setWordWrap(True)  # Enable word wrapping
        self.ai_result.setStyleSheet(
            "font-style: italic; color: #333; padding: 15px; background: #E1BEE7; border-radius: 8px; border: 1px solid #7B1FA2;"
        )
        self.ai_result.setVisible(False)
        self.layout.addWidget(self.ai_result)

    def fetch_all_data(self):
        """Main function that loads all data from the server."""
        symbol = self.symbol_input.text().upper().strip()
        if not symbol:
            return

        self.info_label.setText("טוען נתונים מהשרת...")

        # 1. Get live quote
        try:
            resp = requests.get(f"{SERVER_URL}/stocks/quote/{symbol}")
            if resp.status_code == 200:
                data = resp.json()
                self.info_label.setText(
                    f"מניה: {data['symbol']} | מחיר: ${data['price']}"
                )
                self.save_btn.setEnabled(True)
                self.ai_btn.setEnabled(True)
            else:
                self.info_label.setText("שגיאה: המניה לא נמצאה.")
                return
        except Exception as e:
            self.info_label.setText(f"שגיאת תקשורת: {e}")
            return

        # 2. Get history for the chart
        try:
            hist_resp = requests.get(f"{SERVER_URL}/stocks/history/{symbol}")
            if hist_resp.status_code == 200:
                history_data = hist_resp.json()
                self.update_chart(symbol, history_data)
        except Exception as e:
            print(f"Graph error: {e}")

    def update_chart(self, symbol, data):
        """Build the chart based on the data."""
        series = QLineSeries()
        series.setName(f"מגמת {symbol} (חודש אחרון)")

        # Convert the data into chart points
        # We'll use indices (0,1,2...) as the X axis for simplicity
        for i, point in enumerate(data):
            series.append(i, point["price"])

        # Create chart object
        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()  # Create default axes automatically
        chart.setTitle(f"היסטוריית מחירים: {symbol}")

        # Chart styling
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # Update chart in the window
        self.chart_view.setChart(chart)

    def ask_ai_agent(self):
        """Request AI analysis for the stock."""
        symbol = self.symbol_input.text().upper().strip()
        self.ai_result.setVisible(True)
        self.ai_result.setText("ה-AI חושב... (מתחבר ל-Ollama/Server)")
        QApplication.processEvents()  # Refresh UI

        try:
            resp = requests.get(f"{SERVER_URL}/stocks/analyze/{symbol}")
            if resp.status_code == 200:
                analysis = resp.json().get("analysis", "No analysis")
                self.ai_result.setText(f"💡 ניתוח AI:\n{analysis}")
            else:
                self.ai_result.setText("שגיאה בקבלת ניתוח AI.")
        except Exception as e:
            self.ai_result.setText(f"AI Error: {e}")

    def save_to_cloud(self):
        """Save to the database."""
        symbol = self.symbol_input.text().upper().strip()
        try:
            resp = requests.post(f"{SERVER_URL}/stocks/watchlist/auto?symbol={symbol}")
            if resp.status_code == 200:
                QMessageBox.information(self, "הצלחה", f"המניה {symbol} נשמרה בענן!")
            else:
                QMessageBox.warning(
                    self, "שגיאה", "לא ניתן לשמור (האם תיקנת את הטבלה ב-Supabase?)"
                )
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"תקלה בשמירה: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockClientApp()
    window.show()
    sys.exit(app.exec())
