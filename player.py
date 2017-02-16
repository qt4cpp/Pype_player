import sys
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import (QPalette, QIcon)
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication, QWidget,
                             QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy, QPushButton, QStyle)
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

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)

        displayLayout = QVBoxLayout()
        displayLayout.addWidget(self.videoWidget)
        displayLayout.addLayout(controlLayout)

        self.setLayout(displayLayout)

        self.player.setVideoOutput(self.videoWidget)
        self.player.stateChanged.connect(self.playerStateChanged)


    def open(self):
        fileName = QFileDialog.getOpenFileUrl(self,"Open file", QDir.homePath(), ("Video (*.mp4)"))

        if fileName != "":
            c = QMediaContent(fileName[0])
            self.player.setMedia(c)
            self.player.play()
            self.playButton.setEnabled(True)


    def play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()


    def playerStateChanged(self, state):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


class PypePlayer(QMainWindow):

    def __init__(self, parent=None):
        super(PypePlayer, self).__init__(parent)

        player = Player()
        self.setCentralWidget(player)
        self.createMenus(player)

        self.resize(320, 240)
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
