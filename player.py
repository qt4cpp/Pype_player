import sys
from PyQt5.QtCore import (QDir, Qt, QTime)
from PyQt5.QtGui import (QPalette, QIcon)
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication, QWidget, QLabel,
                             QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy, QPushButton, QStyle,
                             QSlider)
from PyQt5.QtMultimedia import (QMediaPlayer, QMediaContent)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from enum import IntEnum

class SeekStep(IntEnum):
    SHORT = 5
    MEDIUM = 30
    LONG = 60
    VERYLONG = 300


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
        self.volume = 50

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

        self.muteButton = QPushButton()
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume if self.player.isMuted() == False else
                                                          QStyle.SP_MediaVolumeMuted))
        self.muteButton.clicked.connect(self.toggleMute)

        self.volumeBar = QSlider(Qt.Horizontal)
        self.volumeBar.setRange(0, 100)
        self.volumeBar.setValue(self.volume)

        self.labelVolume = QLabel(str(self.volume))
        self.labelVolume.setMinimumWidth(24)

        self.seekBar = QSlider(Qt.Horizontal)
        self.seekBar.setRange(0, self.player.duration() / 1000)

        self.labelTotalTime = QLabel('00:00')
        self.labelCurrentTime = QLabel('00:00')

        seekBarLayout = QHBoxLayout()
        seekBarLayout.addWidget(self.labelCurrentTime)
        seekBarLayout.addWidget(self.seekBar)
        # seekBarLayout.addWidget(self.seekBar, stretch=1)
        seekBarLayout.addWidget(self.labelTotalTime)

        controlWithoutSeekBarLayout = QHBoxLayout()
        controlWithoutSeekBarLayout.addWidget(self.openButton)
        controlWithoutSeekBarLayout.addWidget(self.playButton)
        controlWithoutSeekBarLayout.addWidget(self.stopButton)
        controlWithoutSeekBarLayout.addStretch(stretch=2)
        controlWithoutSeekBarLayout.addWidget(self.muteButton)
        controlWithoutSeekBarLayout.addWidget(self.volumeBar)
        controlWithoutSeekBarLayout.addWidget(self.labelVolume, alignment=Qt.AlignRight)

        controlLayout = QVBoxLayout()
        controlLayout.addLayout(seekBarLayout)
        controlLayout.addLayout(controlWithoutSeekBarLayout)

        displayLayout = QVBoxLayout()
        displayLayout.addWidget(self.videoWidget, QSizePolicy.ExpandFlag)
        displayLayout.addLayout(controlLayout)

        self.setLayout(displayLayout)

        self.player.setVideoOutput(self.videoWidget)

        self.player.stateChanged.connect(self.playerStateChanged)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)

        self.volumeBar.sliderMoved.connect(self.setVolume)
        self.volumeBar.sliderReleased.connect(self.setVolume)
        self.volumeBar.valueChanged.connect(self.volumeChanged)

        self.seekBar.sliderMoved.connect(self.seek)
        self.seekBar.sliderReleased.connect(self.seekBarClicked)


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
            self.seek(0)


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
            currentTimeStr = '00:00'

        self.labelCurrentTime.setText(currentTimeStr)


    def setVolume(self):
        self.player.setVolume(self.volumeBar.sliderPosition())


    def volumeChanged(self):
        self.labelVolume.setText(str(self.volumeBar.sliderPosition()))
        self.volume = self.volumeBar.sliderPosition()


    def seekBarClicked(self):
        self.seek(self.seekBar.sliderPosition())


    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)


    def toggleMute(self):
        if self.player.isMuted():
            self.player.setMuted(False)
            self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        else:
            self.player.setMuted(True)
            self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))

    def forward(self, seconds):
        currentPosition = self.seekBar.sliderPosition()

        if currentPosition + seconds < self.duration:
            self.seek(currentPosition + seconds)
        else:
            self.seek(self.duration)


    def forward_short(self):
        self.forward(SeekStep.SHORT)


    def forward_medium(self):
        self.forward(SeekStep.MEDIUM)


    def forward_long(self):
        self.forward(SeekStep.LONG)


    def forward_verylong(self):
        self.forward(SeekStep.VERYLONG)


class PypePlayer(QMainWindow):

    def __init__(self, parent=None):
        super(PypePlayer, self).__init__(parent)

        player = Player()
        self.setCentralWidget(player)
        self.createMenus(player)

        self.resize(480, 360)
        self.setWindowTitle('Pype Player')
        self.show()


    def createMenus(self, player):
        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+o')
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(player.open)

        forward_short = QAction('Short Forward', self)
        forward_short.setShortcut('Right')
        forward_short.triggered.connect(player.forward_short)
        forward_medium = QAction('Medium Forward', self)
        forward_medium.setShortcut('Shift+Right')
        forward_medium.triggered.connect(player.forward_medium)
        forward_long = QAction('Long Forward', self)
        forward_long.setShortcut('Ctrl+Right')
        forward_long.triggered.connect(player.forward_long)
        forward_verylong = QAction('Very Long Forward', self)
        forward_verylong.setShortcut('Shift+Ctrl+Right')
        forward_verylong.triggered.connect(player.forward_verylong)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        playbackMenu = menubar.addMenu('&Playback')
        playbackMenu.addAction(forward_short)
        playbackMenu.addAction(forward_medium)
        playbackMenu.addAction(forward_long)
        playbackMenu.addAction(forward_verylong)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    pypePlayer = PypePlayer()
    sys.exit(app.exec_())
