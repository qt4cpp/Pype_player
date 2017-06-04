from PyQt5.QtCore import (Qt, QModelIndex, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication, QPushButton, QLabel, QTabWidget, QInputDialog,
                             QMessageBox)

from playlistview import PlaylistView


class PlaylistTab(QTabWidget):

    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.addTab(self.create_new(), 'temp')
        self.setCurrentIndex(0)
        self.setUsesScrollButtons(True)
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.setElideMode(Qt.ElideNone)

        self.show()

    def url(self, index=0):
        self.playListView.url(index)

    def open(self):
        self.widget(self.currentIndex()).open()

    def current_playlist(self):
        return self.currentWidget()

    def add_playlist(self):
        title, ok = QInputDialog.getText(self, 'New Playlist name', 'New Playlist name')
        if ok and len(title) > 0:
            self.addTab(self.create_new(), title)
            return True
        return False

    def create_new(self):
        new = PlaylistView()
        new.playlist_double_clicked.connect(self.handle_playlist_double_clicked)
        return new

    def rename_playlist(self):
        title, ok = QInputDialog.getText(self, 'Rename Playlist', 'New Playlist name')
        if ok and len(str(title)) > 0:
            self.setTabText(self.currentIndex(), title)
            return True
        else:
            return False

    def remove_playlist(self):
        msg_box = QMessageBox()
        if self.count() <= 1:
            return
        current = self.currentIndex()
        msg_box.setText('Do you really want to remove \'{0}\' ?'.format(self.tabText(current)))
        msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        ret = msg_box.exec()
        if ret == QMessageBox.Ok:
            self.removeTab(current)

    def handle_playlist_double_clicked(self):
        self.double_clicked.emit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = PlaylistTab()
    sys.exit(app.exec_())