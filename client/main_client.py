import sys
import os

# הוספת התיקייה הראשית לנתיב (כדי שהאימפורטים יעבדו)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from PySide6.QtWidgets import QApplication
# שים לב: אנחנו מייבאים עכשיו מהקובץ המסודר
from client.app_controller import AppController, GLOBAL_STYLE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # החלת העיצוב שהגדרנו ב-Controller
    app.setStyleSheet(GLOBAL_STYLE)
    
    # יצירת המופע של ה-Controller הראשי
    controller = AppController()
    controller.show()
    
    sys.exit(app.exec())