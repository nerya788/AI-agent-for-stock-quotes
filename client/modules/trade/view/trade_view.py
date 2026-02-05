from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QSpinBox, QComboBox)
from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator, QFont

class TradeView(QWidget):
    on_trade_clicked = Signal(dict)  # קנייה או מכירה
    on_cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.trade_mode = None  # "buy" או "sell"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Trade Stock")
        self.setFixedSize(500, 650)
        
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; }
            QLineEdit { 
                background-color: #313244; border: 1px solid #45475a; 
                padding: 5px 10px; border-radius: 6px; color: white; font-size: 14px; min-height: 35px; 
            }
            QLineEdit:focus { border: 1px solid #89b4fa; background-color: #45475a; }
            QSpinBox {
                background-color: #313244; border: 2px solid #fab387; border-radius: 6px;
                padding: 5px 10px; color: white; font-size: 16px; font-weight: bold; min-height: 27px;
            }
            QSpinBox:focus { border: 2px solid #89b4fa; background-color: #45475a; }
            QComboBox {
                background-color: #313244; border: 1px solid #45475a; 
                padding: 5px 10px; border-radius: 6px; color: white; font-size: 14px; min-height: 20px;
            }
            QComboBox:focus { border: 1px solid #89b4fa; background-color: #45475a; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { width: 12px; height: 12px; }
            QPushButton { 
                padding: 10px; border-radius: 6px; font-weight: bold; font-size: 14px; min-height: 27px; 
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # כותרת
        self.header = QLabel()
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        self.header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header)

        # פרטי מניה
        info_layout = QHBoxLayout()
        self.symbol_label = QLabel("SYMBOL")
        self.symbol_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #89b4fa;")
        
        self.price_label = QLabel("$0.00")
        self.price_label.setStyleSheet("font-size: 28px; color: #fab387;")
        
        info_layout.addWidget(self.symbol_label)
        info_layout.addStretch()
        info_layout.addWidget(self.price_label)
        self.layout.addLayout(info_layout)

        # כמות זמינה (רק למכירה)
        self.available_layout = QHBoxLayout()
        self.available_qty_label = QLabel("Available: 0 shares")
        self.available_qty_label.setStyleSheet("font-size: 14px; color: #a6e3a1;")
        self.available_layout.addWidget(self.available_qty_label)
        self.available_layout.addStretch()
        self.available_widget = QWidget()
        self.available_widget.setLayout(self.available_layout)
        self.layout.addWidget(self.available_widget)

        # כמות
        self.qty_label = QLabel()
        self.qty_label.setStyleSheet("font-size: 14px; color: #cdd6f4; font-weight: bold;")
        self.layout.addWidget(self.qty_label)
        
        qty_layout = QHBoxLayout()
        qty_layout.setSpacing(10)
        
        # כפתור מינוס
        self.minus_btn = QPushButton("−")
        self.minus_btn.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #1e1e2e;
                font-size: 16px;
                font-weight: bold;
                min-width: 20px;
                min-height: 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #f5b9a1; }
            QPushButton:pressed { background-color: #f09660; }
        """)
        
        # תצוגת הכמות
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(1, 10000)
        self.amount_spin.setValue(1)
        self.amount_spin.setSuffix(" shares")
        self.amount_spin.setReadOnly(True)
        self.amount_spin.setButtonSymbols(QSpinBox.NoButtons)
        self.amount_spin.valueChanged.connect(self.update_total)
        
        # כפתור פלוס
        self.plus_btn = QPushButton("+")
        self.plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #1e1e2e;
                font-size: 16px;
                font-weight: bold;
                min-width: 20px;
                min-height: 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #f5b9a1; }
            QPushButton:pressed { background-color: #f09660; }
        """)
        
        self.minus_btn.clicked.connect(lambda: self.amount_spin.setValue(max(1, self.amount_spin.value() - 1)))
        self.plus_btn.clicked.connect(lambda: self.amount_spin.setValue(self.amount_spin.value() + 1))
        
        qty_layout.addWidget(self.minus_btn)
        qty_layout.addWidget(self.amount_spin, 1)
        qty_layout.addWidget(self.plus_btn)
        self.layout.addLayout(qty_layout)

        # סה"כ / הכנסה (קנייה/מכירה)
        self.total_row = QHBoxLayout()
        self.total_label_text = QLabel()
        self.total_label_text.setStyleSheet("font-size: 14px; color: #cdd6f4;")
        self.total_value = QLabel("$0.00")
        self.total_value.setStyleSheet("font-size: 20px; font-weight: bold; color: #a6e3a1;")
        self.total_row.addWidget(self.total_label_text)
        self.total_row.addStretch()
        self.total_row.addWidget(self.total_value)
        self.layout.addLayout(self.total_row)

        # רווח/הפסד (רק למכירה)
        self.pnl_row = QHBoxLayout()
        self.pnl_label_text = QLabel("Profit/Loss:")
        self.pnl_label_text.setStyleSheet("font-size: 14px; color: #cdd6f4;")
        self.pnl_value = QLabel("$0.00")
        self.pnl_value.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1;")
        self.pnl_row.addWidget(self.pnl_label_text)
        self.pnl_row.addStretch()
        self.pnl_row.addWidget(self.pnl_value)
        self.pnl_widget = QWidget()
        self.pnl_widget.setLayout(self.pnl_row)
        self.layout.addWidget(self.pnl_widget)

        self.layout.addWidget(QLabel("Payment Details 💳"))

        # דרופדאון כרטיסים שמורים
        self.saved_cards_combo = QComboBox()
        self.saved_cards_combo.addItem("Enter New Card")
        self.saved_cards_combo.currentIndexChanged.connect(self.on_card_selected)
        self.layout.addWidget(QLabel("Saved Cards:"))
        self.layout.addWidget(self.saved_cards_combo)

        # שם בעל כרטיס
        self.card_holder = QLineEdit()
        self.card_holder.setPlaceholderText("Card Holder Name")
        self.card_holder.setValidator(QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]+")))
        self.layout.addWidget(self.card_holder)

        # מספר כרטיס
        self.card_number = QLineEdit()
        self.card_number.setPlaceholderText("Card Number (16 digits)")
        self.card_number.setMaxLength(16)
        self.card_number.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+")))
        self.layout.addWidget(self.card_number)

        # תוקף ו-CVV
        card_row = QHBoxLayout()
        
        self.expiration = QLineEdit()
        self.expiration.setPlaceholderText("MM/YY")
        self.expiration.setInputMask("99/99;_")
        
        self.cvv = QLineEdit()
        self.cvv.setPlaceholderText("CVV")
        self.cvv.setMaxLength(3)
        self.cvv.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+")))
        
        card_row.addWidget(self.expiration)
        card_row.addWidget(self.cvv)
        self.layout.addLayout(card_row)

        self.layout.addStretch()

        # כפתורים
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #45475a; color: white;")
        self.cancel_btn.clicked.connect(self.on_cancel_clicked.emit)

        self.trade_btn = QPushButton()
        self.trade_btn.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.trade_btn)
        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)
        
        # משתנים פרטיים
        self.current_unit_price = 0.0
        self.buy_price = 0.0
        self.event_id = None
        self.saved_cards = []

    def set_mode(self, mode):
        """הגדרת מצב קנייה או מכירה"""
        self.trade_mode = mode
        
        if mode == "buy":
            self.header.setText("Complete Your Purchase 🛒")
            self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #a6e3a1; margin-bottom: 10px;")
            self.qty_label.setText("Quantity:")
            self.total_label_text.setText("Total Cost:")
            self.available_widget.hide()
            self.pnl_widget.hide()
            self.trade_btn.setText("Buy")
            self.trade_btn.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e;")
            self.trade_btn.clicked.connect(self.handle_buy)
        else:  # sell
            self.header.setText("Sell Your Stock 📊")
            self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #f38ba8; margin-bottom: 10px;")
            self.qty_label.setText("Quantity to Sell:")
            self.total_label_text.setText("Total Income:")
            self.available_widget.show()
            self.pnl_widget.show()
            self.trade_btn.setText("Sell")
            self.trade_btn.setStyleSheet("background-color: #f38ba8; color: #1e1e2e;")
            self.trade_btn.clicked.connect(self.handle_sell)

    def set_stock_data(self, symbol, current_price, available_qty, buy_price, event_id=None):
        """הגדרת נתוני המניה"""
        self.symbol_label.setText(symbol)
        self.price_label.setText(f"${current_price:.2f}")
        self.current_unit_price = current_price
        self.buy_price = buy_price
        self.event_id = event_id
        
        self.available_qty_label.setText(f"Available: {int(available_qty)} shares")
        self.amount_spin.setRange(1, int(available_qty))
        self.amount_spin.setValue(1)
        
        self.update_total()

    def update_total(self):
        """עדכון סכום סה"כ / הכנסה ורווח/הפסד"""
        qty = self.amount_spin.value()
        
        if self.trade_mode == "buy":
            total = qty * self.current_unit_price
            self.total_value.setText(f"${total:,.2f}")
        else:  # sell
            income = qty * self.current_unit_price
            self.total_value.setText(f"${income:,.2f}")
            
            pnl = (self.current_unit_price - self.buy_price) * qty
            self.pnl_value.setText(f"${pnl:,.2f}")
            
            # צביעה לפי רווח או הפסד
            if pnl >= 0:
                self.pnl_value.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1;")
            else:
                self.pnl_value.setStyleSheet("font-size: 18px; font-weight: bold; color: #f38ba8;")

    def handle_buy(self):
        """שליחת בקשת קנייה"""
        data = {
            "symbol": self.symbol_label.text(),
            "price": self.current_unit_price,
            "amount": self.amount_spin.value(),
            "card_holder": self.card_holder.text(),
            "card_number": self.card_number.text(),
            "expiration": self.expiration.text(),
            "cvv": self.cvv.text(),
            "save_card": False,
            "user_id": None
        }
        self.on_trade_clicked.emit(data)

    def handle_sell(self):
        """שליחת בקשת מכירה"""
        data = {
            "symbol": self.symbol_label.text(),
            "current_price": self.current_unit_price,
            "buy_price": self.buy_price,
            "amount": self.amount_spin.value(),
            "event_id": self.event_id,
            "card_holder": self.card_holder.text(),
            "card_number": self.card_number.text(),
            "expiration": self.expiration.text(),
            "cvv": self.cvv.text(),
            "user_id": None
        }
        self.on_trade_clicked.emit(data)

    def load_saved_cards(self, cards):
        """טען כרטיסים שמורים"""
        self.saved_cards = cards
        
        self.saved_cards_combo.blockSignals(True)
        self.saved_cards_combo.clear()
        self.saved_cards_combo.addItem("Enter New Card", None)
        
        if cards and len(cards) > 0:
            for card in cards:
                card_number = card.get('card_number', 'Unknown')
                card_holder = card.get('card_holder', 'Unknown')
                last_four = card_number[-4:] if len(card_number) >= 4 else card_number
                card_display = f"****{last_four} ({card_holder})"
                self.saved_cards_combo.addItem(card_display, card)
        
        self.saved_cards_combo.blockSignals(False)

    def on_card_selected(self, index):
        """כאשר בוחרים כרטיס משמור"""
        if index == 0:
            self.card_holder.clear()
            self.card_number.clear()
            self.expiration.clear()
            self.cvv.clear()
        else:
            card = self.saved_cards_combo.currentData()
            if card:
                self.card_holder.setText(card.get("card_holder", ""))
                self.card_number.setText(card.get("card_number", ""))
                self.expiration.setText(card.get("expiration", ""))
                self.cvv.setText(card.get("cvv", ""))
