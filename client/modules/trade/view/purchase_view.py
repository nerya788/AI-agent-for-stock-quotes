from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QSpinBox, QComboBox)
from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

class PurchaseView(QWidget):
    on_buy_clicked = Signal(dict)
    on_cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Buy Stock")
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
        header = QLabel("Complete Your Purchase 🛒")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #a6e3a1; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # פרטי מניה
        info_layout = QHBoxLayout()
        self.symbol_label = QLabel("SYMBOL")
        self.symbol_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #89b4fa;")
        
        self.price_label = QLabel("$0.00")
        self.price_label.setStyleSheet("font-size: 28px; color: #fab387;")
        
        info_layout.addWidget(self.symbol_label)
        info_layout.addStretch()
        info_layout.addWidget(self.price_label)
        layout.addLayout(info_layout)

        # כמות
        qty_layout = QHBoxLayout()
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(1, 10000)
        self.amount_spin.setValue(1)
        self.amount_spin.setSuffix(" shares")
        self.amount_spin.valueChanged.connect(self.update_total)
        
        qty_layout.addWidget(QLabel("Quantity:"))
        qty_layout.addWidget(self.amount_spin)
        layout.addLayout(qty_layout)

        # סה"כ
        total_row = QHBoxLayout()
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #a6e3a1;")
        total_row.addWidget(QLabel("Total Cost:"))
        total_row.addStretch()
        total_row.addWidget(self.total_label)
        layout.addLayout(total_row)

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
        
        # --- התיקון לולידציית תאריך ---
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

        self.save_card_chk = QCheckBox("Save card securely")
        layout.addWidget(self.save_card_chk)

        layout.addStretch()

        # כפתורים
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #45475a; color: white;")
        self.cancel_btn.clicked.connect(self.on_cancel_clicked.emit)

        self.buy_btn = QPushButton("Confirm Purchase")
        self.buy_btn.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e;")
        self.buy_btn.setCursor(Qt.PointingHandCursor)
        self.buy_btn.clicked.connect(self.handle_buy)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.buy_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.current_unit_price = 0.0
        self.saved_cards = []  # רשימה של כרטיסים שמורים

    def set_stock_data(self, symbol, price):
        self.symbol_label.setText(symbol)
        self.price_label.setText(f"${price:.2f}")
        self.current_unit_price = price
        self.update_total()

    def update_total(self):
        qty = self.amount_spin.value()
        total = qty * self.current_unit_price
        self.total_label.setText(f"${total:,.2f}")

    def handle_buy(self):
        data = {
            "symbol": self.symbol_label.text(),
            "price": self.current_unit_price,
            "amount": self.amount_spin.value(),
            "card_holder": self.card_holder.text(),
            "card_number": self.card_number.text(),
            "expiration": self.expiration.text(),
            "cvv": self.cvv.text(),
            "save_card": self.save_card_chk.isChecked(),
            "user_id": None  # Will be set by trade_controller
        }
        self.on_buy_clicked.emit(data)

    def load_saved_cards(self, cards):
        """טען כרטיסים שמורים מה-API"""
        self.saved_cards = cards
        self.saved_cards_combo.blockSignals(True)
        self.saved_cards_combo.clear()
        self.saved_cards_combo.addItem("Enter New Card")
        
        for card in cards:
            # הצג את 4 הספרות האחרונות של הכרטיס
            card_display = f"****{card['card_number'][-4:]} ({card.get('card_holder', 'Unknown')})"
            self.saved_cards_combo.addItem(card_display, card)
        
        self.saved_cards_combo.blockSignals(False)
        print(f"✅ Loaded {len(cards)} saved cards")

    def on_card_selected(self, index):
        """כאשר בוחרים כרטיס משמור"""
        print(f"🎯 Card selected at index: {index}")
        
        if index == 0:
            # "Enter New Card" selected - clear fields
            print("  → Clearing fields for new card entry")
            self.card_holder.clear()
            self.card_number.clear()
            self.expiration.clear()
            self.cvv.clear()
        else:
            # בחרו כרטיס משמור - מלא את השדות
            card = self.saved_cards_combo.currentData()
            print(f"  → Selected card data: {card}")
            
            if card:
                self.card_holder.setText(card.get("card_holder", ""))
                self.card_number.setText(card.get("card_number", ""))
                self.expiration.setText(card.get("expiration", ""))
                self.cvv.setText(card.get("cvv", ""))
                print(f"  ✅ Filled fields for: {card.get('card_holder')}")