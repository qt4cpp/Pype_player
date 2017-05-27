from PyQt5.QtCore import (Qt, QModelIndex)
from PyQt5.QtWidgets import (QApplication, QPushButton, QLabel, QTabWidget, QInputDialog)

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
        self.using_playlist = self.widget(self.currentIndex())
        return self.using_playlist.current()

    def next(self):
        return self.using_playlist.next()

    def previous(self):
        return self.using_playlist.previous()

    def add_playlist(self):
        title, ok = QInputDialog.getText(self, 'New Playlist name', 'New Playlist name')
        if ok and len(str(title)) > 0:
            self.addTab(PlaylistView(), str(title))
            return True
        else:
            return False


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())