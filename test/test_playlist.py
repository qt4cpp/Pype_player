import unittest

from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout

from playlist import Playlist

class PlaylistTestWidget(QWidget):

    def __init__(self, parent=None):
        super(PlaylistTestWidget, self).__init__(parent)
        self.playlist = Playlist()
        self.add_button = QPushButton('add')
        self.add_button.clicked.connect(self.playlist.add_playlist)

        layout = QVBoxLayout()
        layout.addWidget(self.playlist)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

        self.show()


class TestPlaylist(unittest.TestCase):

    def setUp(self):
        self.playlist = PlaylistTestWidget()

    def test_add(self):
        self.assertEqual(self.playlist.playlist.add_playlist(), True)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = PlaylistTestWidget()

    file_url = []
    current_dir = QDir.current()
    for file in current_dir.entryList():
        if file == '.' or file == '..':
            continue
        file_url.append(QUrl('{0}/{1}'.format(current_dir.absolutePath(), file)))
    playlist.playlist.current().add_items(file_url)

    sys.exit(app.exec_())

