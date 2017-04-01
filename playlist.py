from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QListWidget, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QWidget,
                             QStyle)
from PyQt5.QtMultimedia import QMediaContent, QMediaResource


class Playlist(QWidget):

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)

        self.m_playlist = []
        self.playListView = QListWidget()
        self.openButton = QPushButton('open')

        layout = QVBoxLayout()
        layout.addWidget(self.playListView)
        layout.addWidget(self.openButton)
        self.setLayout(layout)

        self.openButton.clicked.connect(self.open)

        self.show()


    def open(self):
        fileURL, _ = QFileDialog.getOpenFileUrl(self, 'Open File')

        if not fileURL.isEmpty():
            self.m_playlist.append(fileURL)
            print(fileURL)
            self.playListView.addItem(fileURL.fileName())


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())