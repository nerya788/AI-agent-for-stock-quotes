from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt


class BasketView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛒 AI Investment Basket")
        self.setMinimumSize(650, 450)
        self.setStyleSheet(
            "background-color: #1e1e2e; color: #cdd6f4; font-family: Arial;"
        )
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Header ---
        header = QLabel("Review & Adjust Your Investment Plan")
        header.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #89b4fa; margin-bottom: 15px;"
        )
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # --- Stocks table ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Symbol", "Price ($)", "Quantity", "Total ($)"]
        )

        # Table styling
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )  # Prevent regular editing (we'll place a SpinBox)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setStyleSheet(
            """
            QTableWidget {
                background-color: #313244;
                border-radius: 8px;
                gridline-color: #45475a;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #a6e3a1;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """
        )
        layout.addWidget(self.table)

        # --- Total cost ---
        self.total_label = QLabel("Total Estimated Cost: $0.00")
        self.total_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #f9e2af; margin-top: 10px;"
        )
        self.total_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.total_label)

        # --- Confirm / Cancel buttons ---
        btn_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(
            "background-color: #f38ba8; color: #11111b; padding: 12px; font-weight: bold; font-size: 14px; border-radius: 5px;"
        )
        self.cancel_btn.setCursor(Qt.PointingHandCursor)

        self.confirm_btn = QPushButton("Confirm & Execute All 🚀")
        self.confirm_btn.setStyleSheet(
            "background-color: #a6e3a1; color: #11111b; padding: 12px; font-weight: bold; font-size: 14px; border-radius: 5px;"
        )
        self.confirm_btn.setCursor(Qt.PointingHandCursor)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)

        layout.addLayout(btn_layout)
