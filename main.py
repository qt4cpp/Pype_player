import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

from menu_controller import MenuController
from player import Player
from utility import createAction
from viewer import Viewer


class PypePlayer(QMainWindow):

    def __init__(self, parent=None):
        super(PypePlayer, self).__init__(parent)

        self.player = Player(parent=self)
        self.setCentralWidget(self.player)
        self.menu_controller = MenuController(self, self.menuBar())
        self.player.create_menus(self.menu_controller)

        self.player.media_loaded.connect(self.set_window_title)
        self.player.stopped.connect(self.set_window_title)

        self.viewer = Viewer()
        self.viewer.create_menus(self.menu_controller)

        self.resize(600, 360)
        self.set_window_title('')
        self.show()


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
