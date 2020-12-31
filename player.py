from enum import IntEnum

from PySide2.QtCore import (QUrl, Qt, QTime, QTimer, Signal, Slot)
from PySide2.QtGui import (QPalette)
from PySide2.QtMultimedia import (QMediaContent, QMediaPlayer)
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,
                             QStyle, QSlider, QSplitter, QMenu, QComboBox)

from playlist import Playlist
from repeat_control import RepeatControl
from utility import create_flat_button


class SeekStep(IntEnum):
    SHORT = 5
    MEDIUM = 30
    LONG = 300
    VERYLONG = 600


class VideoWidget(QVideoWidget):

    double_clicked = Signal()

    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.setMinimumWidth(150)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()


class Player(QWidget):

    media_loaded = Signal(str)
    stopped = Signal(str)
    playlist_size_changed = Signal(int)
    handle_double_click = Slot()

    def __init__(self, parent=None):
        super(Player, self).__init__(parent)

        self.duration = 0
        self.volume = 50

        self.player = QMediaPlayer()
        self.playlist = Playlist(self)
        self.videoWidget = VideoWidget()
        self.next_url = QUrl()
        self.context_menu = QMenu(self)
        self.display_splitter = QSplitter(Qt.Horizontal)
        self.repeat_control = RepeatControl(parent=self)
        self.repeat_control.get_player_position = self.player.position
        self.repeat_control.set_position_to_player = self.player.setPosition
        self.player.positionChanged.connect(self.repeat_control.set_pos)

        self.setAcceptDrops(True)

        std_icon = self.style().standardIcon
        self.play_button = create_flat_button(std_icon(QStyle.SP_MediaPlay))
        self.stopButton = create_flat_button(std_icon(QStyle.SP_MediaStop), '')
        self.backwardButton = create_flat_button(std_icon(QStyle.SP_MediaSkipBackward), '')
        self.forwardButton = create_flat_button(std_icon(QStyle.SP_MediaSkipForward), '')

        self.order_list = self.repeat_control.menu()
        self.order_list.setFixedWidth(115)

        self.playback_rate_menu = QComboBox()
        self.playback_rate_menu.addItems((
            '0.5x', '0.75x', '0.9x', '1.0x', '1.1x', '1.25x', '1.5x'))
        self.playback_rate_menu.setCurrentText('1.0x')

        self.muteButton = create_flat_button(std_icon(
            QStyle.SP_MediaVolume if not self.player.isMuted() else QStyle.SP_MediaVolumeMuted))

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
        controlWithoutSeekBarLayout.addWidget(self.playback_rate_menu)
        controlWithoutSeekBarLayout.addStretch(stretch=2)
        controlWithoutSeekBarLayout.addWidget(self.muteButton)
        controlWithoutSeekBarLayout.addWidget(self.volumeBar)
        controlWithoutSeekBarLayout.addWidget(self.labelVolume, alignment=Qt.AlignRight)

        controlLayout = QVBoxLayout()
        controlLayout.addLayout(seekBarLayout)
        controlLayout.addLayout(controlWithoutSeekBarLayout)

        self.display_splitter.setOpaqueResize(False)
        self.display_splitter.addWidget(self.videoWidget)
        self.display_splitter.addWidget(self.playlist.widget)
        self.display_splitter.setSizes([300, 200])

        layout = QVBoxLayout()
        layout.setContentsMargins(11, 0, 11, 0)
        layout.addWidget(self.display_splitter, 1)
        layout.addLayout(controlLayout)
        layout.addWidget(self.repeat_control.ab_repeat_widget)
        layout.addWidget(self.statusInfoLabel)

        self.setLayout(layout)

    def create_connections(self):
        self.play_button.clicked.connect(self.optimal_play)
        self.stopButton.clicked.connect(self.stop)
        self.backwardButton.clicked.connect(self.skip_backward)
        self.forwardButton.clicked.connect(self.skip_forward)
        self.muteButton.clicked.connect(self.toggleMute)
        self.playback_rate_menu.currentTextChanged.connect(self.set_playback_rate)

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

        self.repeat_control.pos_exceeded.connect(self.seek)
        self.player.currentMediaChanged.connect(self.repeat_control.reset)

        self.playlist.double_clicked.connect(self.load_and_play)

        self.videoWidget.double_clicked.connect(self.no_future)

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def no_future(self):
        self.display_splitter.moveSplitter(0, 1)

    def autoplay(self):
        """メディアを読み込み、再生する。

        order_listに応じて、次に何を再生するかを決める。
        """
        i = self.order_list.currentIndex()
        if i == 1:
            # self.repeat_track()
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
            self.media_loaded.emit(self.playlist.current_title())
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
            self.seek(0)
            self.player.stop()
            self.setStatusInfo('Stopped')
            self.stopped.emit('')

    def playerStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


    def durationChanged(self, duration):
        self.repeat_control.set_duration(duration)
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
        QTimer.singleShot(50, self.play)

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

    def set_playback_rate(self, rate_text):
        self.player.setPlaybackRate(float(rate_text[:-1]))

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
        url = self.playlist.previous()
        if url is None:
            return None
        else:
            self.load(url)

    def skip_forward(self):
        self.next_track()
        self.play()

    def skip_backward(self):
        if self.seekBar.sliderPosition() > 2:
            self.seek(0)
        else:
            self.previous_track()
            self.play()

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            self.load(urls[0])
            # self.stop()
            self.play()

