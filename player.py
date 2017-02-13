import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QPalette, QIcon)
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication, QWidget,
                             QHBoxLayout, QFileDialog, QSizePolicy)
from PyQt5.QtMultimedia import (QMediaPlayer, QMediaContent)
from PyQt5.QtMultimediaWidgets import QVideoWidget


class VideoWidget(QVideoWidget):

    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

class Player(QWidget):

    def __init__(self, parent=None):

        super(Player, self).__init__(parent)

        self.player = QMediaPlayer()

        self.videoWidget = VideoWidget()
        self.player.setVideoOutput(self.videoWidget)

        displayLayout = QHBoxLayout()
        displayLayout.addWidget(self.videoWidget)

        self.setLayout(displayLayout)


    def open(self):
        fileName = QFileDialog.getOpenFileUrl(self,"Open file", "~/", ("Video (*.mp4 *.wmv)"))
        c = QMediaContent(fileName[0])
        self.player.setMedia(c)
        self.player.setVolume(50)
        self.player.play()


class PypePlayer(QMainWindow):

    def __init__(self, parent=None):
        super(PypePlayer, self).__init__(parent)

        player = Player()
        self.setCentralWidget(player)
        self.createMenus(player)

        self.setGeometry(300, 300, 350,  300)
        self.setWindowTitle('Pype Player')
        self.show()


    def createMenus(self, player):
        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+o')
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(player.open)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    pypePlayer = PypePlayer()
    sys.exit(app.exec_())
