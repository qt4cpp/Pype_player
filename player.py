import sys
from PyQt5.QtCore import (QUrl, Qt, QTime, QTimer, pyqtSignal)
from PyQt5.QtGui import (QPalette, QIcon)
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication, QWidget, QLabel,
                             QHBoxLayout, QVBoxLayout, QSizePolicy, QPushButton, QStyle,
                             QSlider, QListView)
from PyQt5.QtMultimedia import (QMediaPlayer, QMediaContent, QMediaPlaylist)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from enum import IntEnum
from utility import createAction
from playlist import Playlist

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

    media_loaded = pyqtSignal()

    def __init__(self, parent=None):
        super(Player, self).__init__(parent)

        self.duration = 0
        self.volume = 50

        self.player = QMediaPlayer()
        self.playList = Playlist()
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

        self.statusInfoLabel = QLabel()

        self.seekBar = QSlider(Qt.Horizontal)
        self.seekBar.setRange(0, self.player.duration() / 1000)

        self.labelTotalTime = QLabel('00:00')
        self.labelCurrentTime = QLabel('00:00')


        seekBarLayout = QHBoxLayout()
        seekBarLayout.addWidget(self.labelCurrentTime)
        seekBarLayout.addWidget(self.seekBar)
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
        displayLayout.addWidget(self.playList)

        layout = QVBoxLayout()
        layout.addLayout(displayLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusInfoLabel)

        self.setLayout(layout)

        self.player.setVideoOutput(self.videoWidget)

        self.player.stateChanged.connect(self.playerStateChanged)
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)

        self.player.error.connect(self.handleError)

        self.volumeBar.sliderMoved.connect(self.setVolume)
        self.volumeBar.sliderReleased.connect(self.setVolume)
        self.volumeBar.valueChanged.connect(self.volumeChanged)

        self.seekBar.sliderMoved.connect(self.seek)
        self.seekBar.sliderReleased.connect(self.seekBarClicked)

        self.playList.playListView.current_index_changed.connect(self.load_and_play)
        self.media_loaded.connect(self.playList.playListView.update)

        self.videoWidget.show()

    def open(self):
        self.playList.open()
        if self.playList.playListView.count() > 0:
            self.enableInterface()

    def load_and_play(self):
        """メディアを読み込み、再生する。"""
        #TODO: NoMedia以外でもメディアをロードしないと次にいけない。
        if self.player.mediaStatus() == QMediaPlayer.NoMedia:
            self.load(self.playList.current())
            self.play()
        else:
            self.load(self.playList.current())
            self.player.play()

    def load(self, file_url: QUrl):
        if file_url is None:
            self.stop()
            return False
        c = QMediaContent(file_url)
        self.player.setMedia(c)
        self.media_loaded.emit()
        self.enableInterface()

    def play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        elif self.player.mediaStatus() == QMediaPlayer.NoMedia:
            return
        elif self.player.mediaStatus() == QMediaPlayer.LoadingMedia\
            or self.player.mediaStatus() == QMediaPlayer.StalledMedia:
            QTimer.singleShot(500, self.player.play)
        else:
            self.player.play()


    def stop(self):
        if not self.player.state() == QMediaPlayer.StoppedState:
            self.player.stop()
            self.seek(0)
            self.setStatusInfo('Stopped')

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


    def next(self):
        self.playList.next()


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


    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.LoadingMedia:
            self.setStatusInfo('Loading...')
        elif status == QMediaPlayer.LoadedMedia:
           self.setStatusInfo('Loaded')
        elif status == QMediaPlayer.BufferingMedia:
            self.setStatusInfo('Buffering')
        elif status == QMediaPlayer.EndOfMedia:
            self.player.parent()
            self.stop()
            self.next()
        elif status == QMediaPlayer.InvalidMedia:
            self.handleError()
            self.next()

    def clearStatusInfo(self):
        self.statusInfoLabel.setText("")


    def handleError(self):
        self.disableInterface()
        self.setStatusInfo('Error: ' + self.player.errorString())


    def setStatusInfo(self, message, seconds=5):
        if not message == '':
            self.statusInfoLabel.setText(message)
            QTimer.singleShot(seconds*1000, self.clearStatusInfo)


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

        self.resize(600, 360)
        self.setWindowTitle('Pype Player')
        self.show()


    def createMenus(self, player):
        openFile = createAction(self, 'Open', player.playList.open, 'Ctrl+o')
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
