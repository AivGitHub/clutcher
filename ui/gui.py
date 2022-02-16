from PyQt5.QtWidgets import QMainWindow

from ui.generated import Ui_MainFrame
from clutcher import settings


class MainFrame(QMainWindow, Ui_MainFrame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.setupUi(self)

    def retranslateUi(self, MainFrame):
        super().retranslateUi(MainFrame)
        MainFrame.setWindowTitle(settings.NAME.capitalize())
