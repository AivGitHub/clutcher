from concurrent.futures import ThreadPoolExecutor
import pathlib
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
import threading

from clutcher import settings
from torrent.structure.torrent import Torrent
from ui.generated import Ui_MainFrame


class MainFrame(QMainWindow, Ui_MainFrame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        self.setupUi(self)

        # Triggers
        self.action_Add_Files.triggered.connect(self.add_files)
        self.action_Exit.triggered.connect(self.close)


    def retranslateUi(self, MainFrame):
        super().retranslateUi(MainFrame)
        MainFrame.setWindowTitle(settings.NAME.capitalize())

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        # TODO: Should be not self.tr, but translate because must be an event!
        reply = QMessageBox.question(self, 'Message', self.tr('Are you sure to quit?'), QMessageBox.Yes,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def process(self, torrent: Torrent) -> None:
        # self.save_to_database(torrent)
        print(f'Task Executed {threading.current_thread()}')

    def add_files(self) -> None:
        files = QFileDialog.getOpenFileNames(self, 'Open a file', '', 'All Files (*.*)')
        files = files[0]
        broken_files = []
        torrents = []

        for file in files:
            try:
                torrents.append(Torrent(file))
            except Exception as e:
                broken_files.append(pathlib.Path(file).name)
                pass

        if broken_files:
            self.show_message(f'Errors for files: {", ".join(broken_files)} have occurred.', _type='error')

        with ThreadPoolExecutor() as executor:
            running_tasks = [executor.submit(self.process, torrent) for torrent in torrents]

            for running_task in running_tasks:
                running_task.result()

    def show_message(self, message: str, _type: str = 'message', text_color: str = None) -> None:
        if text_color:
            self.statusBar().setStyleSheet(f'color : {text_color}')
            self.statusbar.showMessage(message)
            return None

        if _type == 'error':
            text_color = 'red'
        elif _type == 'message':
            text_color = 'black'
        else:
            text_color = 'black'

        self.statusBar().setStyleSheet(f'color : {text_color}')
        self.statusbar.showMessage(message)
