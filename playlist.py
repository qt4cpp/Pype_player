from PyQt5.QtCore import (Qt, QModelIndex)
from PyQt5.QtWidgets import (QApplication, QPushButton, QLabel, QTabWidget, QInputDialog,
                             QMessageBox)

from playlistview import PlaylistView


class Playlist(QTabWidget):

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)

        self.addTab(PlaylistView(), 'temp')
        self.setCurrentIndex(0)

        self.using_playlist = self.widget(0)

        self.show()

    def url(self, index=0):
        self.playListView.url(index)

    def current(self):
        self.using_playlist = self.currentWidget()
        return self.using_playlist.current()

    def next(self):
        return self.using_playlist.next()

    def previous(self):
        return self.using_playlist.previous()

    def open(self):
        self.currentWidget().open()

    def count_items(self):
        return self.currentWidget().count()

    def add_playlist(self):
        title, ok = QInputDialog.getText(self, 'New Playlist name', 'New Playlist name')
        if ok and len(str(title)) > 0:
            self.addTab(PlaylistView(), str(title))
            return True
        else:
            return False

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


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())