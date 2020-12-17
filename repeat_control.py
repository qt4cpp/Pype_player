from PySide2.QtCore import QObject, QTime, Slot, Signal, QTimer
from PySide2.QtWidgets import QComboBox, QWidget, QTimeEdit, QHBoxLayout, QLabel, QStyle, \
    QApplication, QPushButton

from utility import create_flat_button, ms_to_qtime, qtime_to_ms


class RepeatControl(QObject):
    """
    repeat 機能を担うクラス。メニューの提供も行う。

    AB-repeat をする際に時間を取得し、プレイヤーからは現在の位置を取得し、
    指定した時間に達すると、pos_exceeded signalを発する。
    AB_repeat_
    """
    item_name = ('No repeat', 'Repeat track', 'Repeat all', 'A-B repeat')
    pos_exceeded = Signal(int)
    time_changed = Signal(QTime, QTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu_box = QComboBox(parent)
        self.menu_box.addItems(self.item_name)
        self.ab_repeat_widget = ABRepeatWidget()
        self.a_time = QTime(0, 0)
        self.b_time = QTime(0, 0)
        self.duration = QTime(0, 0)
        self.current = QTime()
        self.monitoring_timer = QTimer(self)

        # Connect
        self.menu_box.currentIndexChanged.connect(self.handle_menu_changed)
        self.handle_menu_changed(self.menu_box.currentIndex())
        self.ab_repeat_widget.a_time.timeChanged.connect(self.set_a_time)
        self.ab_repeat_widget.b_time.timeChanged.connect(self.set_b_time)
        self.monitoring_timer.timeout.connect(self.monitor_pos)

    def menu(self):
        """
        GUI用のメニューを返す。
        :return:
        """
        return self.menu_box

    def handle_menu_changed(self, index: int):
        """
        If AB-repeat is chosen, the widget shows, otherwise hides.
        """
        if index == 0:  # Repeat 機能 Off
            self.reset()
            self.ab_repeat_widget.hide()
            self.monitor_deactivate()
        elif index == 1:
            self.ab_repeat_widget.hide()
            self.set_b_time(QTime(ms_to_qtime(qtime_to_ms(self.duration) - 500)))
        elif index == 3:
            self.reset()
            self.ab_repeat_widget.show()
        else:
            self.ab_repeat_widget.hide()
            self.monitor_deactivate()

    @Slot(int)
    def set_pos(self, pos):
        """
        プレイヤーの現在位置を監視する。
        """
        self.current = ms_to_qtime(pos)

    def monitor_pos(self):
        """
        b-time の値がセットされた動作する関数。
        現在位置がb-time を超えるとシグナルを発する。
        シグナルには、戻す時間が入っている。
        """
        if self.current >= self.b_time:
            target = int(qtime_to_ms(self.a_time) / 1000)
            self.pos_exceeded.emit(target)

    def set_a_time(self, time):
        self.a_time = time
        self.timer_is_valid()

    def set_b_time(self, time):
        self.b_time = time
        self.timer_is_valid()

    def timer_is_valid(self):
        if self.b_time > self.a_time:
            self.monitor_activate()
        else:
            self.monitor_deactivate()

    def set_duration(self, ms):
        self.duration = ms_to_qtime(ms)
        self.ab_repeat_widget.b_time.setMaximumTime(self.duration)

    def reset(self):
        self.a_time = QTime(0, 0)
        self.b_time = QTime(0, 0)
        self.ab_repeat_widget.reset()

    def monitor_activate(self):
        self.monitoring_timer.start(400)  # monitoring 間隔を指定する。

    def monitor_deactivate(self):
        self.monitoring_timer.stop()


class ABRepeatWidget(QWidget):
    """
    A-B間リピートの時間指定を受け付けるウィジェット。
    開始時間と終了時間を指定し、それをプレイヤーに伝える。
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.a_label = QLabel('Start:')
        self.a_time = QTimeEdit(self)
        self.a_time.setDisplayFormat('hh:mm:ss')
        icon = self.style().standardIcon(QStyle.SP_ArrowDown)
        self.set_pos_to_a_btn = create_flat_button(icon)
        self.b_label = QLabel('End:')
        self.b_time = QTimeEdit(self)
        self.b_time.setDisplayFormat('hh:mm:ss')
        self.set_pos_to_b_btn = create_flat_button(icon)
        self.reset_btn = QPushButton('Reset', parent=self)

        self.reset_btn.pressed.connect(self.reset)

        self.create_layout()

    def create_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(11, 0, 11, 0)
        layout.addWidget(self.a_label)
        layout.addWidget(self.a_time)
        layout.addWidget(self.set_pos_to_a_btn)
        layout.addSpacing(30)
        layout.addWidget(self.b_label)
        layout.addWidget(self.b_time)
        layout.addWidget(self.set_pos_to_b_btn)
        layout.addWidget(self.reset_btn)
        layout.addStretch(1)
        self.setLayout(layout)

    def set_pos_to_a(self, ms: int):
        """
        時間を TimeEdit widget にセットする。
        ms はmillisecondsで与えられること。 6の1.5倍
        """
        self.a_time.setTime(QTime(ms=ms))

    def set_pos_to_b(self, ms: int):
        self.b_time.setTime(QTime(ms=ms))

    def reset(self):
        self.a_time.setTime(QTime(0, 0))
        self.b_time.setTime(QTime(0, 0))

    def hide(self) -> None:
        self.reset()
        super().hide()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    w = RepeatControl()
    w.ab_repeat_widget.b_time.setTime(QTime(0, 1, s=10, ms=900))
    w.ab_repeat_widget.show()
    w.ab_repeat_widget.reset()
    sys.exit(app.exec_())
