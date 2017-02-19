import sys
from PyQt5.QtCore import QDir, Qt, QTime
from PyQt5.QtGui import (QPalette, QIcon)
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication, QWidget, QLabel,
                             QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy, QPushButton, QStyle,
                             QSlider)
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

        self.duration = 0

        self.player = QMediaPlayer()

        self.videoWidget = VideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.stopButton = QPushButton()
        self.stopButton.setEnabled(False)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.clicked.connect(self.stop)

        self.openButton = QPushButton()
        self.openButton.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.openButton.clicked.connect(self.open)

        self.seekBar = QSlider(Qt.Horizontal)
        self.seekBar.setRange(0, self.player.duration() / 1000)

        self.labelTotalTime = QLabel()
        self.labelCurrentTime = QLabel()

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.addWidget(self.labelCurrentTime)
        controlLayout.addWidget(self.seekBar)
        controlLayout.addWidget(self.labelTotalTime)

        displayLayout = QVBoxLayout()
        displayLayout.addWidget(self.videoWidget, QSizePolicy.ExpandFlag)
        displayLayout.addLayout(controlLayout)

        self.setLayout(displayLayout)

        self.player.setVideoOutput(self.videoWidget)

        self.player.stateChanged.connect(self.playerStateChanged)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)

        self.seekBar.sliderMoved.connect(self.seek)
        self.seekBar.sliderReleased.connect(self.seekBarMoved)


    def open(self):
        fileUrl, _ = QFileDialog.getOpenFileUrl(self,"Open file", QDir.homePath(), ("Video (*.mp4)"))

        if fileUrl.isEmpty() == False:
            c = QMediaContent(fileUrl)
            self.player.setMedia(c)
            self.player.play()
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)


    def play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()


    def stop(self):
        if not self.player.state() == QMediaPlayer.StoppedState:
            self.player.stop()


    def playerStateChanged(self, state):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


    def durationChanged(self, duration):
        duration /= 1000

        self.duration = duration

        totalTime = QTime((duration/3600)%60, (duration/60)%60, (duration%60), (duration*1000)%1000)

        format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
        totalTimeStr = totalTime.toString(format)

        self.labelTotalTime.setText(totalTimeStr)
        self.seekBar.setMaximum(duration)


    def positionChanged(self, progress):
        progress /= 1000

        self.updateCurrentTime(progress)
        self.seekBar.setValue(progress)


    def updateCurrentTime(self, currentInfo):
        if currentInfo:
            currentTime = QTime((currentInfo/3600)%60, (currentInfo/60)%60,
                                currentInfo%60, (currentInfo*1000)%1000)

            format = 'hh:mm:ss' if self.duration > 3600 else 'mm:ss'
            currentTimeStr = currentTime.toString(format)
        else:
            currentTimeStr = ''

        self.labelCurrentTime.setText(currentTimeStr)


    def seekBarMoved(self):
        self.seek(self.seekBar.sliderPosition())


    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)


#        def setTimetoLabel(self, )


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
