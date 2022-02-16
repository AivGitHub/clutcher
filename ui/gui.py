from PyQt5.QtWidgets import QMainWindow, QMessageBox

from ui.generated import Ui_MainFrame
from clutcher import settings


class MainFrame(QMainWindow, Ui_MainFrame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        self.setupUi(self)

    def retranslateUi(self, MainFrame):
        super().retranslateUi(MainFrame)
        MainFrame.setWindowTitle(settings.NAME.capitalize())

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        # TODO: Should me not self.tr, but translate because must be a event!
        reply = QMessageBox.question(self, 'Message', self.tr('Are you sure to quit?'), QMessageBox.Yes,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
