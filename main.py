import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

from player import Player
from utility import createAction


class PypePlayer(QMainWindow):

    def __init__(self, parent=None):
        super(PypePlayer, self).__init__(parent)

        player = Player()
        self.setCentralWidget(player)
        self.createMenus(player)

        self.resize(600, 360)
        self.setWindowTitle('Pype Player')
        self.show()


    def createMenus(self, player):
        openFile = createAction(self, 'Open', player.open, 'Ctrl+o')

        add_playlist = createAction(self, 'Add playlist', player.playlist_tab.add_playlist, 'Ctrl+N')
        rename_playlist = createAction(self, 'Rename Playlist', player.playlist_tab.rename_playlist)
        remove_playlist = createAction(self, 'Remove Playlist', player.playlist_tab.remove_playlist)

        forward_short = createAction(self, 'Short Forward', player.forward_short, 'Right')
        forward_medium = createAction(self, 'Forward', player.forward_medium, 'Shift+Right')
        forward_long = createAction(self, 'Long Forward', player.forward_long, 'Ctrl+Right')
        forward_verylong = createAction(self, 'Very Long Forward', player.forward_verylong, 'Shift+Ctrl+Right')
        backward_short = createAction(self, 'Short Backward', player.backward_short, 'Left')
        backward_medium = createAction(self, 'Backward', player.backward_medium, 'Shift+Left')
        backward_long = createAction(self, 'Long Backward', player.backward_long, 'Ctrl+Left')
        backward_verylong = createAction(self, 'Very Long Backward', player.backward_verylong, 'Shift+Ctrl+Left')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addSeparator()
        fileMenu.addAction(add_playlist)
        fileMenu.addAction(rename_playlist)
        fileMenu.addAction(remove_playlist)

        playbackMenu = menubar.addMenu('&Playback')
        jumpMenu = playbackMenu.addMenu('Jump')
        jumpMenu.addAction(forward_short)
        jumpMenu.addAction(forward_medium)
        jumpMenu.addAction(forward_long)
        jumpMenu.addAction(forward_verylong)
        jumpMenu.addSeparator()
        jumpMenu.addAction(backward_short)
        jumpMenu.addAction(backward_medium)
        jumpMenu.addAction(backward_long)
        jumpMenu.addAction(backward_verylong)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    pypePlayer = PypePlayer()
    sys.exit(app.exec_())
