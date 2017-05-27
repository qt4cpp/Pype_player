from PyQt5.QtCore import (Qt, QModelIndex)
from PyQt5.QtWidgets import (QApplication, QPushButton, QLabel, QTabWidget)

from playlistview import PlaylistView


class Playlist(QTabWidget):

    @property
    def count(self):
        return self.playListView.count()

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)

        self.addTab(PlaylistView(), 'temp')
        self.addTab(PlaylistView(), 'test')
        self.count_label = QLabel()
        self.playListView = self.widget(0)

        # layout = QVBoxLayout()
        # layout.addWidget(self.playListView)
        # layout.addWidget(self.count_label, alignment=Qt.AlignRight)
        # self.setLayout(layout)

        self.count_label_update()
        self.playListView.current_index_changed.connect(self.count_label_update)
        self.playListView.model().rowCount_changed.connect(self.count_label_update)

        self.show()

    def debugUI(self):
        self.openButton = QPushButton('open')
        self.debugButton = QPushButton('m_playlist')

        layout = self.layout()
        layout.addWidget(self.openButton)
        layout.addWidget(self.debugButton)

        self.openButton.clicked.connect(self.open)
        self.debugButton.clicked.connect(self.debug_m_playlist)

    def open(self):
        self.playListView.open()

    def url(self, index=0):
        self.playListView.url(index)

    def current(self):
        return self.playListView.current()

    def next(self):
        return self.playListView.next()

    def previous(self):
        return self.playListView.previous()

    def set_current_index(self, index):
        isSuccess = self.playListView.set_current_index_from_row(index)
        return isSuccess

    def count_label_update(self):
        self.count_label.setText('{0}/{1}'.format(
            self.playListView.current_row+1, self.playListView.count()))

    def debug_m_playlist(self):
        print('rowCount: ', self.playListView.model().rowCount())
        for row in range(self.playListView.model().rowCount()):
            index = self.playListView.model().index(row, 0, QModelIndex())
            print('m_playlist:\n', self.playListView.model().data(index, Qt.DisplayRole))


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    playlist.debugUI()
    sys.exit(app.exec_())