import os

from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout


class settings_widget(QWidget):
    """設定へのアクセスをするインターフェイスを提供する"""

    def __init__(self, parent=None):
        super().__init__(parent)

        settings = QSettings()

        file_group = QGroupBox('File:')
        self.path_line = QLineEdit(self)
        self.path_button = QPushButton('Choose...', self)

        self.path_line.setPlaceholderText("Enter your path")
        self.path_line.setText = settings.value('settings_file_path', os.getcwd())

        self.save_button = QPushButton('Save', self)
        self.cancel_button = QPushButton('Cancel', self)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_line)
        path_layout.addWidget(self.path_button)
        file_group.setLayout(path_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        glayout = QGridLayout()
        glayout.addWidget(file_group, 0, 0, 1, 0)
        glayout.addLayout(button_layout, 1, 1)

        self.setLayout(glayout)
