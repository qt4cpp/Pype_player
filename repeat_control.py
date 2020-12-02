from PySide2.QtCore import QObject
from PySide2.QtWidgets import QComboBox, QWidget


class RepeatControl:
    """
    repeat 機能を担うクラス。
    メニューの提供と再生のコントロールをする。
    """
    def __init__(self, parent):
        super().__init__()
        self.menu_box = QComboBox(parent)
        self.menu_box.addItems(('No repeat', 'Repeat track', 'Repeat all', 'A-B repeat'))

    def menu(self):
        """
        GUI用のメニューを返す。
        :return:
        """
        return self.menu_box


class ABRepeatWidget(QWidget):
    """
    A-B間リピートの時間指定を受け付けるウィジェット。
    開始時間と終了時間を指定し、それをプレイヤーに伝える。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
