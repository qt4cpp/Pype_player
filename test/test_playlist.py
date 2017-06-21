import unittest

from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout

from playlisttab import PlaylistTab

class PlaylistTestWidget(QWidget):

    def __init__(self, parent=None):
        super(PlaylistTestWidget, self).__init__(parent)
        self.playlist_tab = PlaylistTab()
        self.add_button = QPushButton('add')
        self.add_button.clicked.connect(self.playlist_tab.add_playlist)
        self.save_button = QPushButton('save')
        self.save_button.clicked.connect(self.playlist_tab.save_current)
        self.save_all_button = QPushButton('save all')
        self.save_all_button.clicked.connect(self.playlist_tab.save_all)

        layout = QVBoxLayout()
        layout.addWidget(self.playlist_tab)
        layout.addWidget(self.add_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.save_all_button)
        self.setLayout(layout)

        self.show()


class TestPlaylist(unittest.TestCase):

    def setUp(self):
        self.playlist = PlaylistTestWidget()

    def test_add(self):
        self.assertEqual(self.playlist.playlist_tab.add_playlist(), True)


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
    playlist.playlist_tab.currentWidget().add_items(file_url)

    unittest.main()
    sys.exit(app.exec_())

