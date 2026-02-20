import sys
import os

# Add the project root to sys.path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from PySide6.QtWidgets import QApplication

# Note: we now import from the organized file
from client.app_controller import AppController, GLOBAL_STYLE

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply the global style defined in the controller
    app.setStyleSheet(GLOBAL_STYLE)

    # Create the main controller instance
    controller = AppController()
    controller.show()

    sys.exit(app.exec())
