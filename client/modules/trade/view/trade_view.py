from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator, QFont


class TradeView(QWidget):
    on_trade_clicked = Signal(dict)
    on_cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.trade_mode = "buy"
        self.current_unit_price = 0.0
        self.buy_price = 0.0
        self.event_id = None
        self.saved_cards_data = []
        self.init_ui()

    def init_ui(self):
        # Change 1: remove fixed size to avoid clipping
        self.setMinimumSize(450, 650)
        self.resize(500, 700)

        self.setStyleSheet(
            """
            QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; }
            QLineEdit, QComboBox { 
                background-color: #313244; border: 1px solid #45475a; 
                padding: 5px; border-radius: 6px; color: white; font-size: 14px; min-height: 30px; 
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #89b4fa; background-color: #45475a; }
            
            /* Change 2: medium-sized buttons (not huge, not tiny) */
            QPushButton.qty-btn {
                background-color: #fab387; color: #1e1e2e; font-size: 16px; font-weight: bold;
                border-radius: 6px; min-width: 30px; min-height: 30px; margin: 0px;
            }
            QPushButton.qty-btn:hover { background-color: #f5c2a5; }

            QPushButton.action-btn { 
                padding: 10px; border-radius: 6px; font-weight: bold; font-size: 15px; min-height: 40px; 
            }
            
            QSpinBox { 
                background: transparent; border: none; color: white; font-size: 18px; font-weight: bold; 
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(10)  # Reduce spacing
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.header = QLabel("Trade Stock")
        self.header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header)

        # Info frame
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #313244; border-radius: 8px; padding: 5px;"
        )
        info_layout = QHBoxLayout(info_frame)

        self.symbol_label = QLabel("SYMBOL")
        self.symbol_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #89b4fa; border: none;"
        )
        self.price_label = QLabel("$0.00")
        self.price_label.setStyleSheet("font-size: 24px; color: #fab387; border: none;")

        info_layout.addWidget(self.symbol_label)
        info_layout.addStretch()
        info_layout.addWidget(self.price_label)
        layout.addWidget(info_frame)

        # Status labels
        self.available_label = QLabel("")
        self.available_label.setStyleSheet("color: #a6e3a1; font-size: 13px;")
        layout.addWidget(self.available_label)

        self.pnl_label = QLabel("")
        layout.addWidget(self.pnl_label)

        layout.addSpacing(5)

        # Quantity section
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantity:"))
        qty_layout.addStretch()

        self.btn_minus = QPushButton("−")
        self.btn_minus.setProperty("class", "qty-btn")
        self.btn_minus.setCursor(Qt.PointingHandCursor)
        self.btn_minus.clicked.connect(self._decrease_qty)

        self.amount_spin = QSpinBox()
        self.amount_spin.setAlignment(Qt.AlignCenter)
        self.amount_spin.setButtonSymbols(QSpinBox.NoButtons)
        self.amount_spin.setRange(1, 100000)
        self.amount_spin.setValue(1)
        self.amount_spin.setFixedWidth(80)  # Fixed width for consistent layout
        self.amount_spin.valueChanged.connect(self.update_total)

        self.btn_plus = QPushButton("+")
        self.btn_plus.setProperty("class", "qty-btn")
        self.btn_plus.setCursor(Qt.PointingHandCursor)
        self.btn_plus.clicked.connect(self._increase_qty)

        qty_layout.addWidget(self.btn_minus)
        qty_layout.addWidget(self.amount_spin)
        qty_layout.addWidget(self.btn_plus)
        layout.addLayout(qty_layout)

        # Total
        total_layout = QHBoxLayout()
        self.total_title = QLabel("Total:")
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #a6e3a1;"
        )
        total_layout.addWidget(self.total_title)
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)

        layout.addWidget(QLabel("Payment Details 💳"))

        self.saved_cards_combo = QComboBox()
        self.saved_cards_combo.addItem("Enter New Card")
        self.saved_cards_combo.currentIndexChanged.connect(self.on_card_selected)
        layout.addWidget(self.saved_cards_combo)

        # Card fields
        self.card_widget = QWidget()
        card_layout = QVBoxLayout(self.card_widget)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(8)

        self.card_holder = QLineEdit()
        self.card_holder.setPlaceholderText("Card Holder Name")
        # Validation 1: letters only
        self.card_holder.setValidator(
            QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]+"))
        )

        self.card_number = QLineEdit()
        self.card_number.setPlaceholderText("Card Number (16 digits)")
        self.card_number.setMaxLength(16)
        # Validation 2: digits only
        self.card_number.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9]+"))
        )

        row_expiry = QHBoxLayout()
        self.expiration = QLineEdit()
        self.expiration.setPlaceholderText("MM/YY")
        self.expiration.setInputMask("99/99;_")

        self.cvv = QLineEdit()
        self.cvv.setPlaceholderText("CVV")
        self.cvv.setMaxLength(3)
        self.cvv.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+")))

        row_expiry.addWidget(self.expiration)
        row_expiry.addWidget(self.cvv)

        card_layout.addWidget(self.card_holder)
        card_layout.addWidget(self.card_number)
        card_layout.addLayout(row_expiry)
        layout.addWidget(self.card_widget)

        self.save_card_chk = QCheckBox("Save card for future")
        layout.addWidget(self.save_card_chk)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(
            "background-color: #45475a; padding: 10px; border-radius: 6px;"
        )
        self.cancel_btn.clicked.connect(self.on_cancel_clicked.emit)

        self.action_btn = QPushButton("CONFIRM")
        self.action_btn.setProperty("class", "action-btn")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.handle_action)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.action_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    # --- Logic ---
    def _increase_qty(self):
        self.amount_spin.setValue(self.amount_spin.value() + 1)

    def _decrease_qty(self):
        val = self.amount_spin.value()
        if val > 1:
            self.amount_spin.setValue(val - 1)

    def set_mode(self, mode):
        self.trade_mode = mode
        if mode == "buy":
            self.header.setText("Buy Stock")
            self.header.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #a6e3a1;"
            )
            self.action_btn.setText("BUY NOW")
            self.action_btn.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e;")
            self.available_label.hide()
            self.pnl_label.hide()
            self.amount_spin.setRange(1, 100000)
        else:
            self.header.setText("Sell Stock")
            self.header.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #f38ba8;"
            )
            self.action_btn.setText("SELL NOW")
            self.action_btn.setStyleSheet("background-color: #f38ba8; color: #1e1e2e;")
            self.available_label.show()
            self.pnl_label.show()

    def set_stock_data(
        self, symbol, current_price, available_qty=0, buy_price=0, event_id=None
    ):
        self.symbol_label.setText(symbol)
        self.price_label.setText(f"${current_price:.2f}")
        self.current_unit_price = current_price
        self.buy_price = buy_price
        self.event_id = event_id

        if self.trade_mode == "sell":
            self.amount_spin.setRange(1, int(available_qty))
            self.amount_spin.setValue(1)
            self.available_label.setText(f"Available: {int(available_qty)}")
            diff = current_price - buy_price
            color = "#a6e3a1" if diff >= 0 else "#f38ba8"
            self.pnl_label.setText(f"Bought: ${buy_price:.2f} | P/L: ${diff:.2f}")
            self.pnl_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.update_total()

    def update_total(self):
        total = self.amount_spin.value() * self.current_unit_price
        self.total_label.setText(f"${total:,.2f}")

    def load_saved_cards(self, cards):

        self.saved_cards_data = cards

        # Reset the combo box
        self.saved_cards_combo.blockSignals(True)
        self.saved_cards_combo.clear()
        self.saved_cards_combo.addItem("Enter New Card")  # Index 0

        # If list is empty, stop here
        if not cards:
            self.saved_cards_combo.blockSignals(False)
            return

        # Add cards
        for i, card in enumerate(cards):
            last4 = card.get("card_number", "????")[-4:]
            self.saved_cards_combo.addItem(f"**** {last4}")

        self.saved_cards_combo.blockSignals(False)

        if self.saved_cards_combo.count() > 1:
            self.saved_cards_combo.setCurrentIndex(1)

            # Manually trigger field fill
            self.on_card_selected(1)

    def on_card_selected(self, index):
        if index == 0:
            self.card_holder.clear()
            self.card_number.clear()
            self.expiration.clear()
            self.cvv.clear()
        elif index - 1 < len(self.saved_cards_data):
            card = self.saved_cards_data[index - 1]
            self.card_holder.setText(card.get("card_holder", ""))
            self.card_number.setText(card.get("card_number", ""))
            self.expiration.setText(card.get("expiration", ""))
            self.cvv.setText(card.get("cvv", ""))

    def handle_action(self):
        # --- Change 3: strict validation before submitting ---
        if not self.card_holder.text().strip():
            QMessageBox.warning(self, "Error", "Card Holder Name is required.")
            return

        if len(self.card_number.text()) != 16:
            QMessageBox.warning(self, "Error", "Card number must be 16 digits.")
            return

        # Validate expiry date (month 1-12)
        exp = (
            self.expiration.text()
        )  # With input mask this will be something like "12/25"
        try:
            month = int(exp.split("/")[0])
            if month < 1 or month > 12:
                QMessageBox.warning(self, "Error", "Invalid Month (01-12).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid Date.")
            return

        data = {
            "symbol": self.symbol_label.text(),
            "price": self.current_unit_price,
            "current_price": self.current_unit_price,
            "amount": self.amount_spin.value(),
            "card_holder": self.card_holder.text(),
            "card_number": self.card_number.text(),
            "expiration": self.expiration.text(),
            "cvv": self.cvv.text(),
            "save_card": self.save_card_chk.isChecked(),
            "buy_price": self.buy_price,
            "event_id": self.event_id,
        }
        self.on_trade_clicked.emit(data)
