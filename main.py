import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

from player import Player
from utility import createAction


class PypePlayer(QMainWindow):

    def __init__(self, parent=None):
        super(PypePlayer, self).__init__(parent)

        self.player = Player(parent=self)
        self.setCentralWidget(self.player)
        self.create_menus()

        self.player.media_loaded.connect(self.set_window_title)
        self.player.stopped.connect(self.set_window_title)

        self.resize(600, 360)
        self.set_window_title('')
        self.show()

    def create_menus(self):

        forward_short = createAction(self, 'Short Forward', self.player.forward_short, 'Right')
        forward_medium = createAction(self, 'Forward', self.player.forward_medium, 'Shift+Right')
        forward_long = createAction(self, 'Long Forward', self.player.forward_long, 'Ctrl+Right')
        forward_verylong = createAction(self, 'Very Long Forward',
                                        self.player.forward_verylong, 'Shift+Ctrl+Right')
        backward_short = createAction(self, 'Short Backward', self.player.backward_short, 'Left')
        backward_medium = createAction(self, 'Backward', self.player.backward_medium, 'Shift+Left')
        backward_long = createAction(self, 'Long Backward', self.player.backward_long, 'Ctrl+Left')
        backward_verylong = createAction(self, 'Very Long Backward',
                                         self.player.backward_verylong, 'Shift+Ctrl+Left')

        play_and_pause = createAction(self, 'Play', self.player.optimal_play, 'Space')
        load_and_play = createAction(self, 'Load and Play', self.player.load_and_play, 'Return')
        self.addAction(load_and_play)

        menubar = self.menuBar()
        self.player.playlist.create_menu(menubar)

        playbackMenu = menubar.addMenu('&Playback')
        playbackMenu.addAction(play_and_pause)
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

    def set_window_title(self, str=''):
        if str:
            self.setWindowTitle('{0} - Pype Player'.format(str))
        else:
            self.setWindowTitle('Pype Player')
        
    def closeEvent(self, event):
        # self.player.playlist.save_all()
        super(PypePlayer, self).closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    pypePlayer = PypePlayer()
    sys.exit(app.exec_())
