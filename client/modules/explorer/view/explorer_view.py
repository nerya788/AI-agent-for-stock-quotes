from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QMessageBox)
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

class ExplorerView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # --- כותרת ---
        header = QLabel("Market Explorer & AI Agent 📈")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #89b4fa; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # --- שורת חיפוש ---
        search_layout = QHBoxLayout()
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter Symbol (e.g. NVDA, TSLA)")
        self.symbol_input.setStyleSheet("padding: 8px; border-radius: 5px; color: white; background: #313244;")
        
        self.search_btn = QPushButton("Search & Analyze 🔍")
        self.search_btn.setStyleSheet("background-color: #89b4fa; color: #1e1e2e; padding: 8px; font-weight: bold;")

        search_layout.addWidget(self.symbol_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # --- תצוגת נתונים (מחיר) ---
        self.info_label = QLabel("Search for a stock to see live data...")
        self.info_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #cdd6f4;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # --- גרף (QtCharts) ---
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(400)
        self.chart_view.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.chart_view)

        # --- כפתורי פעולה (AI, Save, Back) ---
        actions_layout = QHBoxLayout()
        
        self.ai_btn = QPushButton("🤖 Ask AI Agent")
        self.ai_btn.setStyleSheet("background-color: #cba6f7; color: #1e1e2e; padding: 10px; font-weight: bold;")
        self.ai_btn.setEnabled(False) 

        self.save_btn = QPushButton("☁️ Save to Watchlist")
        self.save_btn.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; padding: 10px; font-weight: bold;")
        self.save_btn.setEnabled(False)

        # ... בתוך actions_layout ...
        self.trade_btn = QPushButton("💰 Buy Stock")
        self.trade_btn.setStyleSheet("background-color: #fab387; color: #1e1e2e; padding: 10px; font-weight: bold;")
        self.trade_btn.setEnabled(False) # לא פעיל עד שמוצאים מניה

        self.back_btn = QPushButton("⬅️ Back to Dashboard")
        self.back_btn.setStyleSheet("background-color: #45475a; color: white; padding: 10px;")

        actions_layout.addWidget(self.ai_btn)
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.back_btn)
        actions_layout.addWidget(self.trade_btn)
        layout.addLayout(actions_layout)

        # --- תוצאת ה-AI ---
        self.ai_result = QLabel("")
        self.ai_result.setWordWrap(True)
        self.ai_result.setStyleSheet("font-style: italic; color: #cdd6f4; padding: 15px; background: #313244; border-radius: 8px; border: 1px solid #cba6f7;")
        self.ai_result.setVisible(False)
        layout.addWidget(self.ai_result)

        self.setLayout(layout)

    def plot_chart(self, symbol, data):
        """פונקציית עזר לציור הגרף (מופעלת ע"י הקונטרולר)"""
        series = QLineSeries()
        series.setName(f"{symbol} Trend (1 Month)")
        
        # המרת הנתונים לנקודות
        for i, point in enumerate(data):
            series.append(i, point['price'])

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle(f"Price History: {symbol}")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # התאמת צבעים ל-Dark Mode
        chart.setBackgroundBrush(Qt.NoBrush)
        chart.setTitleBrush(Qt.white)
        chart.legend().setLabelColor(Qt.white)
        
        # עדכון הצירים שיהיו לבנים (קצת טריקי ב-QtCharts, זה הבסיס)
        axis_x = chart.axes(Qt.Horizontal)[0]
        axis_y = chart.axes(Qt.Vertical)[0]
        axis_x.setLabelsColor(Qt.white)
        axis_y.setLabelsColor(Qt.white)

        self.chart_view.setChart(chart)