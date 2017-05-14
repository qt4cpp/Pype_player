import unittest

from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtWidgets import QWidget, QApplication

from playlist import Playlist
from playlistmodel import PlaylistModel


class TestPlaylist(unittest.TestCase):

    def setUp(self):
        self.playlist = Playlist()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    playlist.debugUI()

    current_dir = QDir.current()
    for file in current_dir.entryList():
        if file == '.' or file == '..':
            continue
        file_url = QUrl('{0}/{1}'.format(current_dir.absolutePath(), file))
        playlist.m_playlist.add(file_url)

    sys.exit(app.exec_())

