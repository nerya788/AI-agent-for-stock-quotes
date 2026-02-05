from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QSpinBox, QComboBox)
from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

class SaleView(QWidget):
    on_sell_clicked = Signal(dict)
    on_cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Sell Stock")
        self.setFixedSize(500, 650)
        
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; }
            QLineEdit { 
                background-color: #313244; border: 1px solid #45475a; 
                padding: 5px 10px; border-radius: 6px; color: white; font-size: 14px; min-height: 35px; 
            }
            QLineEdit:focus { border: 1px solid #89b4fa; background-color: #45475a; }
            QSpinBox {
                background-color: #313244; border: 1px solid #fab387; border-radius: 6px;
                padding: 5px; color: white; font-size: 16px; font-weight: bold; min-height: 35px;
            }
            QComboBox {
                background-color: #313244; border: 1px solid #45475a; 
                padding: 5px 10px; border-radius: 6px; color: white; font-size: 14px; min-height: 35px;
            }
            QComboBox:focus { border: 1px solid #89b4fa; background-color: #45475a; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { width: 12px; height: 12px; }
            QPushButton { 
                padding: 10px; border-radius: 6px; font-weight: bold; font-size: 14px; min-height: 40px; 
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # כותרת
        header = QLabel("Sell Your Stock 📊")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #f38ba8; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # פרטי מניה
        info_layout = QHBoxLayout()
        self.symbol_label = QLabel("SYMBOL")
        self.symbol_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #89b4fa;")
        
        self.current_price_label = QLabel("$0.00")
        self.current_price_label.setStyleSheet("font-size: 28px; color: #fab387;")
        
        info_layout.addWidget(self.symbol_label)
        info_layout.addStretch()
        info_layout.addWidget(self.current_price_label)
        layout.addLayout(info_layout)

        # כמות זמינה
        available_layout = QHBoxLayout()
        self.available_qty_label = QLabel("Available: 0 shares")
        self.available_qty_label.setStyleSheet("font-size: 14px; color: #a6e3a1;")
        available_layout.addWidget(self.available_qty_label)
        available_layout.addStretch()
        layout.addLayout(available_layout)

        # כמות למכירה
        qty_layout = QHBoxLayout()
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(1, 10000)
        self.amount_spin.setValue(1)
        self.amount_spin.setSuffix(" shares")
        self.amount_spin.valueChanged.connect(self.update_total)
        
        qty_layout.addWidget(QLabel("Quantity to Sell:"))
        qty_layout.addWidget(self.amount_spin)
        layout.addLayout(qty_layout)

        # סה"כ הכנסה
        income_row = QHBoxLayout()
        self.income_label = QLabel("$0.00")
        self.income_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #a6e3a1;")
        income_row.addWidget(QLabel("Total Income:"))
        income_row.addStretch()
        income_row.addWidget(self.income_label)
        layout.addLayout(income_row)

        # רווח/הפסד
        pnl_row = QHBoxLayout()
        self.pnl_label = QLabel("$0.00")
        self.pnl_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1;")
        pnl_row.addWidget(QLabel("Profit/Loss:"))
        pnl_row.addStretch()
        pnl_row.addWidget(self.pnl_label)
        layout.addLayout(pnl_row)

        layout.addWidget(QLabel("Payment Details 💳"))

        # דרופדאון כרטיסים שמורים
        self.saved_cards_combo = QComboBox()
        self.saved_cards_combo.addItem("Enter New Card")
        self.saved_cards_combo.currentIndexChanged.connect(self.on_card_selected)
        layout.addWidget(QLabel("Saved Cards:"))
        layout.addWidget(self.saved_cards_combo)

        # שם בעל כרטיס
        self.card_holder = QLineEdit()
        self.card_holder.setPlaceholderText("Card Holder Name")
        self.card_holder.setValidator(QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]+")))
        layout.addWidget(self.card_holder)

        # מספר כרטיס (16 ספרות)
        self.card_number = QLineEdit()
        self.card_number.setPlaceholderText("Card Number (16 digits)")
        self.card_number.setMaxLength(16)
        self.card_number.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+")))
        layout.addWidget(self.card_number)

        # תוקף ו-CVV
        row = QHBoxLayout()
        
        self.expiration = QLineEdit()
        self.expiration.setPlaceholderText("MM/YY")
        self.expiration.setInputMask("99/99;_")
        
        self.cvv = QLineEdit()
        self.cvv.setPlaceholderText("CVV")
        self.cvv.setMaxLength(3)
        self.cvv.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+")))
        
        row.addWidget(self.expiration)
        row.addWidget(self.cvv)
        layout.addLayout(row)

        layout.addStretch()

        # כפתורים
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #45475a; color: white;")
        self.cancel_btn.clicked.connect(self.on_cancel_clicked.emit)

        self.sell_btn = QPushButton("Confirm Sale")
        self.sell_btn.setStyleSheet("background-color: #f38ba8; color: #1e1e2e;")
        self.sell_btn.setCursor(Qt.PointingHandCursor)
        self.sell_btn.clicked.connect(self.handle_sell)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.sell_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.current_unit_price = 0.0
        self.buy_price = 0.0  # מחיר הקנייה המקורי
        self.saved_cards = []  # רשימה של כרטיסים שמורים

    def set_stock_data(self, symbol, current_price, available_qty, buy_price):
        """הגדרת נתוני המניה למכירה"""
        self.symbol_label.setText(symbol)
        self.current_price_label.setText(f"${current_price:.2f}")
        self.current_unit_price = current_price
        self.buy_price = buy_price
        
        self.available_qty_label.setText(f"Available: {int(available_qty)} shares")
        self.amount_spin.setRange(1, int(available_qty))
        self.amount_spin.setValue(1)
        
        self.update_total()

    def update_total(self):
        """עדכון סכום ההכנסה והרווח/הפסד"""
        qty = self.amount_spin.value()
        
        # הכנסה מהמכירה
        income = qty * self.current_unit_price
        self.income_label.setText(f"${income:,.2f}")
        
        # רווח/הפסד (מחיר מכירה - מחיר קנייה) * כמות
        pnl = (self.current_unit_price - self.buy_price) * qty
        self.pnl_label.setText(f"${pnl:,.2f}")
        
        # צביעה לפי רווח או הפסד
        if pnl >= 0:
            self.pnl_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1;")
        else:
            self.pnl_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f38ba8;")

    def handle_sell(self):
        """שליחת בקשת המכירה"""
        data = {
            "symbol": self.symbol_label.text(),
            "current_price": self.current_unit_price,
            "buy_price": self.buy_price,
            "amount": self.amount_spin.value(),
            "card_holder": self.card_holder.text(),
            "card_number": self.card_number.text(),
            "expiration": self.expiration.text(),
            "cvv": self.cvv.text(),
            "user_id": None  # Will be set by sale_controller
        }
        self.on_sell_clicked.emit(data)

    def load_saved_cards(self, cards):
        """טען כרטיסים שמורים מה-API"""
        self.saved_cards = cards
        
        # בטל את ה-signal לפני שנתחיל להשנות את הcombo box
        self.saved_cards_combo.blockSignals(True)
        
        # ניקוי ו-reset של הcombo box
        self.saved_cards_combo.clear()
        self.saved_cards_combo.addItem("Enter New Card", None)
        
        # הוסף את כל הכרטיסים
        if cards and len(cards) > 0:
            for card in cards:
                card_number = card.get('card_number', 'Unknown')
                card_holder = card.get('card_holder', 'Unknown')
                
                # הצג את 4 הספרות האחרונות של הכרטיס
                last_four = card_number[-4:] if len(card_number) >= 4 else card_number
                card_display = f"****{last_four} ({card_holder})"
                
                # השמור את הכרטיס כ-data במקום של ה-item
                self.saved_cards_combo.addItem(card_display, card)
                print(f"➕ Added card to dropdown: {card_display}")
        
        # חבר את ה-signal בחזרה
        self.saved_cards_combo.blockSignals(False)
        
        print(f"✅ Loaded {len(cards)} saved cards to dropdown")

    def on_card_selected(self, index):
        """כאשר בוחרים כרטיס משמור"""
        if index == 0:
            # "Enter New Card" selected - clear fields
            self.card_holder.clear()
            self.card_number.clear()
            self.expiration.clear()
            self.cvv.clear()
        else:
            # בחרו כרטיס משמור - מלא את השדות
            card = self.saved_cards_combo.currentData()
            if card:
                self.card_holder.setText(card.get("card_holder", ""))
                self.card_number.setText(card.get("card_number", ""))
                self.expiration.setText(card.get("expiration", ""))
                self.cvv.setText(card.get("cvv", ""))
