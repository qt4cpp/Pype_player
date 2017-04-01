import sys
from PyQt5.QtCore import (QDir, Qt, QTime, QTimer)
from PyQt5.QtGui import (QPalette, QIcon)
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication, QWidget, QLabel,
                             QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy, QPushButton, QStyle,
                             QSlider, QListView)
from PyQt5.QtMultimedia import (QMediaPlayer, QMediaContent, QMediaPlaylist)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from enum import IntEnum
from utility import createAction

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

        self.playList = QMediaPlaylist()
        self.player.setPlaylist(self.playList)

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

        self.backwardButton = QPushButton()
        self.backwardButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.backwardButton.clicked.connect(self.backward_short)
        self.forwardButton = QPushButton()
        self.forwardButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.forwardButton.clicked.connect(self.forward_short)

        self.muteButton = QPushButton()
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume if self.player.isMuted() == False else
                                                          QStyle.SP_MediaVolumeMuted))
        self.muteButton.clicked.connect(self.toggleMute)

        self.volumeBar = QSlider(Qt.Horizontal)
        self.volumeBar.setRange(0, 100)
        self.volumeBar.setValue(self.volume)

        self.labelVolume = QLabel(str(self.volume))
        self.labelVolume.setMinimumWidth(24)

        self.errorLabel = QLabel()

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
        controlWithoutSeekBarLayout.setSpacing(0)
        controlWithoutSeekBarLayout.addWidget(self.openButton)
        controlWithoutSeekBarLayout.addWidget(self.playButton)
        controlWithoutSeekBarLayout.addWidget(self.stopButton)
        controlWithoutSeekBarLayout.addWidget(self.backwardButton)
        controlWithoutSeekBarLayout.addWidget(self.forwardButton)
        controlWithoutSeekBarLayout.addStretch(stretch=2)
        controlWithoutSeekBarLayout.addWidget(self.muteButton)
        controlWithoutSeekBarLayout.addWidget(self.volumeBar)
        controlWithoutSeekBarLayout.addWidget(self.labelVolume, alignment=Qt.AlignRight)

        controlLayout = QVBoxLayout()
        controlLayout.addLayout(seekBarLayout)
        controlLayout.addLayout(controlWithoutSeekBarLayout)

        displayLayout = QHBoxLayout()
        displayLayout.setSpacing(5)
        displayLayout.addWidget(self.videoWidget, QSizePolicy.ExpandFlag)
        self.listview = QListView()
        displayLayout.addWidget(self.listview)

        layout = QVBoxLayout()
        layout.addLayout(displayLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        self.setLayout(layout)

        self.player.setVideoOutput(self.videoWidget)

        self.player.stateChanged.connect(self.playerStateChanged)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)

        self.player.error.connect(self.handleError)

        self.volumeBar.sliderMoved.connect(self.setVolume)
        self.volumeBar.sliderReleased.connect(self.setVolume)
        self.volumeBar.valueChanged.connect(self.volumeChanged)

        self.seekBar.sliderMoved.connect(self.seek)
        self.seekBar.sliderReleased.connect(self.seekBarClicked)

        self.videoWidget.show()


    def open(self):
        fileUrl, _ = QFileDialog.getOpenFileUrl(
            self, 'Open file', QDir.homePath(),
            '*.mp4 *.m4v *.mov *.mpg *.mpeg *.mp3 *.m4a *.wmv')

        if fileUrl.isEmpty() == False:
            c = QMediaContent(fileUrl)
            self.playList.addMedia(c)
            self.player.setMedia(c)

            self.enableInterface()


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


    def disableInterface(self):
        self.playButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.backwardButton.setEnabled(False)
        self.forwardButton.setEnabled(False)
        self.labelCurrentTime.setText('00:00')
        self.labelTotalTime.setText('00:00')


    def enableInterface(self):
        self.playButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.backwardButton.setEnabled(True)
        self.forwardButton.setEnabled(True)


    def clearErrorLabel(self):
        self.errorLabel.setText("")


    def handleError(self):
        self.disableInterface()
        self.errorLabel.setText('Error: ' + self.player.errorString())
        QTimer.singleShot(5000, self.clearErrorLabel)


    def forward(self, seconds):
        currentPosition = self.seekBar.sliderPosition()

        if currentPosition + seconds < self.duration:
            self.seek(currentPosition + seconds)
        else:
            self.seek(self.duration)


    def backward(self, seconds):
        self.forward(-seconds)


    def forward_short(self):
        self.forward(SeekStep.SHORT)


    def forward_medium(self):
        self.forward(SeekStep.MEDIUM)


    def forward_long(self):
        self.forward(SeekStep.LONG)


    def forward_verylong(self):
        self.forward(SeekStep.VERYLONG)

    def backward_short(self):
        self.backward(SeekStep.SHORT)


    def backward_medium(self):
        self.backward(SeekStep.MEDIUM)


    def backward_long(self):
        self.backward(SeekStep.LONG)


    def backward_verylong(self):
        self.backward(SeekStep.VERYLONG)


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
        openFile = createAction(self, 'Open', player.open, 'Ctrl+o')
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
