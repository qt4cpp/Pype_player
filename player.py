from enum import IntEnum

import qtawesome
from PyQt5.QtCore import (QUrl, Qt, QTime, QTimer, pyqtSignal, pyqtSlot, QSize)
from PyQt5.QtGui import (QPalette, QCloseEvent)
from PyQt5.QtMultimedia import (QMediaContent, QMediaPlayer)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QPushButton,
                             QStyle, QSlider, QSplitter, QMenu, QComboBox)

from playlist import Playlist
from playlisttab import PlaylistTab
from utility import make_button_from_fa


class SeekStep(IntEnum):
    SHORT = 5
    MEDIUM = 30
    LONG = 300
    VERYLONG = 600


class VideoWidget(QVideoWidget):

    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.setMinimumWidth(150)


class Player(QWidget):

    media_loaded = pyqtSignal()
    stop = pyqtSignal()
    handle_double_click = pyqtSlot()

    def __init__(self, parent=None):
        super(Player, self).__init__(parent)

        self.duration = 0
        self.volume = 50

        self.player = QMediaPlayer()
        self.playlist = Playlist()
        self.videoWidget = VideoWidget()
        self.next_url = QUrl()

        std_icon = self.style().standardIcon
        self.play_button = QPushButton(std_icon(QStyle.SP_MediaPlay), '')
        self.play_button.setFlat(True)
        self.play_button.setFixedSize(30, 30)

        self.stopButton = QPushButton(std_icon(QStyle.SP_MediaStop), '')
        self.stopButton.setFlat(True)
        self.stopButton.setFixedSize(30, 30)

        self.backwardButton = QPushButton(std_icon(QStyle.SP_MediaSeekBackward), '')
        self.backwardButton.setFlat(True)
        self.backwardButton.setFixedSize(30, 30)
        self.forwardButton = QPushButton(std_icon(QStyle.SP_MediaSeekForward), '')
        self.forwardButton.setFlat(True)
        self.forwardButton.setFixedSize(30, 30)

        self.order_list = QComboBox()
        self.order_list.addItem('No repeat')
        self.order_list.addItem('Repeat track')
        self.order_list.addItem('Repeat all')
        self.order_list.setFixedWidth(115)

        self.muteButton = QPushButton()
        self.muteButton.setIcon(std_icon(
            QStyle.SP_MediaVolume if not self.player.isMuted() else QStyle.SP_MediaVolumeMuted))
        self.muteButton.setFlat(True)
        self.muteButton.setFixedSize(30, 30)

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

        self.create_layout()
        self.create_connections()

        self.player.setVideoOutput(self.videoWidget)
        self.videoWidget.show()

    def create_layout(self):
        seekBarLayout = QHBoxLayout()
        seekBarLayout.addWidget(self.labelCurrentTime)
        seekBarLayout.addWidget(self.seekBar)
        seekBarLayout.addWidget(self.labelTotalTime)

        controlWithoutSeekBarLayout = QHBoxLayout()
        controlWithoutSeekBarLayout.setSpacing(1)
        controlWithoutSeekBarLayout.addWidget(self.play_button)
        controlWithoutSeekBarLayout.addWidget(self.stopButton)
        controlWithoutSeekBarLayout.addWidget(self.backwardButton)
        controlWithoutSeekBarLayout.addWidget(self.forwardButton)
        controlWithoutSeekBarLayout.addWidget(self.order_list)
        controlWithoutSeekBarLayout.addStretch(stretch=2)
        controlWithoutSeekBarLayout.addWidget(self.muteButton)
        controlWithoutSeekBarLayout.addWidget(self.volumeBar)
        controlWithoutSeekBarLayout.addWidget(self.labelVolume, alignment=Qt.AlignRight)

        controlLayout = QVBoxLayout()
        controlLayout.addLayout(seekBarLayout)
        controlLayout.addLayout(controlWithoutSeekBarLayout)

        display_splitter = QSplitter(Qt.Horizontal)
        display_splitter.setOpaqueResize(False)
        display_splitter.addWidget(self.videoWidget)
        display_splitter.addWidget(self.playlist)
        display_splitter.setSizes([300, 200])

        layout = QVBoxLayout()
        layout.addWidget(display_splitter, 1)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusInfoLabel)
        layout.setSpacing(5)

        self.setLayout(layout)

    def create_connections(self):
        self.play_button.clicked.connect(self.optimal_play)
        self.stopButton.clicked.connect(self.stop)
        self.backwardButton.clicked.connect(self.backward_short)
        self.forwardButton.clicked.connect(self.forward_short)
        self.muteButton.clicked.connect(self.toggleMute)

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

        self.playlist.double_clicked.connect(self.load_and_play)

    def autoplay(self):
        """メディアを読み込み、再生する。

        order_listに応じて、次に何を再生するかを決める。
        """
        i = self.order_list.currentIndex()
        if i == 1:
            self.repeat_track()
            return
        elif i == 2:
            self.repeat_all()
        else:
            self.next_track()
        self.play()

    def optimal_play(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            self.load_and_play()
        else:
            self.play()

    def load_and_play(self):
        self.load(self.playlist.get_new_one())
        self.play()

    def load(self, file_url: QUrl):
        if file_url is None:
            return None
        if file_url.isValid():
            c = QMediaContent(file_url)
            self.player.setMedia(c)
            self.media_loaded.emit()
            self.enableInterface()

    def play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            return
        if self.player.mediaStatus() == QMediaPlayer.LoadingMedia or\
                self.player.mediaStatus() == QMediaPlayer.StalledMedia:
            QTimer.singleShot(600, self.player.play)

        self.player.play()
        self.playlist.update_listview()

    def stop(self):
        if not self.player.state() == QMediaPlayer.StoppedState:
            self.player.stop()
            self.seek(0)
            self.setStatusInfo('Stopped')

    def playerStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


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

    def repeat_track(self):
        QTimer.singleShot(100, self.play)

    def repeat_all(self):
        if self.playlist.count()-1 == self.playlist.current_row():
            url = self.playlist.first()
            self.load(url)
        else:
            self.next_track()

    def setVolume(self):
        self.player.setVolume(self.volumeBar.sliderPosition()*2)


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
        self.play_button.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.backwardButton.setEnabled(False)
        self.forwardButton.setEnabled(False)
        self.labelCurrentTime.setText('00:00')
        self.labelTotalTime.setText('00:00')


    def enableInterface(self):
        self.play_button.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.backwardButton.setEnabled(True)
        self.forwardButton.setEnabled(True)


    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.LoadingMedia:
            self.setStatusInfo('Loading...')
        elif status == QMediaPlayer.BufferingMedia:
            self.setStatusInfo('Buffering')
        elif status == QMediaPlayer.EndOfMedia:
            # self.player.stop()
            self.autoplay()
        elif status == QMediaPlayer.InvalidMedia:
            self.handleError()
            #TODO: Step Forward を割り当てる

    def clearStatusInfo(self):
        self.statusInfoLabel.setText("")


    def handleError(self):
        self.disableInterface()
        self.setStatusInfo('Error: ' + self.player.errorString())


    def setStatusInfo(self, message, seconds=5):
        if not message == '':
            self.statusInfoLabel.setText(message)
            QTimer.singleShot(seconds*1000, self.clearStatusInfo)

    def next_track(self):
        url = self.playlist.next()
        if url is None:
            return None
        else:
            self.load(url)

    def previous_track(self):
        pass


    def forward(self, seconds):
        currentPosition = self.seekBar.sliderPosition()

        if currentPosition + seconds < self.duration:
            self.seek(currentPosition + seconds)
        else:
            self.seek(self.duration-1)


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

