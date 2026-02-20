from PySide6.QtCore import QThread, Signal


class WorkerThread(QThread):
    """
    Runs functions in a background thread to keep the UI responsive.
    """

    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # Run the heavy function
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
