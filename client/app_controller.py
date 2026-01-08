from PySide6.QtWidgets import QMainWindow, QStackedWidget
# שים לב: אנחנו ניצור את ה-Controllers האלו בשלב הבא
# from client.modules.auth.controllers.auth_controller import AuthController
# from client.modules.portfolio.controllers.portfolio_controller import PortfolioController

class AppController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockQuotes AI - Enterprise Edition")
        self.setFixedSize(1000, 750)
        
        # המרכז של האפליקציה
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # כאן בעתיד נאתחל את המודולים (Modules)
        # self.auth_module = AuthController(self)
        # self.portfolio_module = PortfolioController(self)