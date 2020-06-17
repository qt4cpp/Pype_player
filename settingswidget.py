import os

from PySide2.QtCore import QSettings
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QDialog, QCheckBox


class settings_widget(QDialog):
    """設定へのアクセスをするインターフェイスを提供する"""

    def __init__(self, parent=None):
        super().__init__(parent)

        settings = QSettings()

        # setting relative to file
        file_group = QGroupBox('Playlist File:')
        self.path_line = QLineEdit(self)
        self.path_button = QPushButton('Choose...', self)

        self.path_line.setPlaceholderText("Enter your path")
        self.path_line.setText(
            settings.value('settings_file_path', os.getcwd())+'/playlist/')

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_line)
        path_layout.addWidget(self.path_button)
        file_group.setLayout(path_layout)

        # player setting
        player_group = QGroupBox('Player Settings:')
        self.play_time_checkbox = QCheckBox('Display remaining time instead of duration.')

        player_layout = QVBoxLayout()
        player_layout.addWidget(self.play_time_checkbox)
        player_group.setLayout(player_layout)

        # Bottom button
        self.save_button = QPushButton('Save', self)
        self.cancel_button = QPushButton('Cancel', self)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.cancel_button)

        glayout = QGridLayout()
        glayout.addWidget(file_group, 0, 0, 1, 2)
        glayout.addWidget(player_group, 1, 0, 1, 2)
        glayout.addLayout(bottom_layout, 2, 1)

        self.setLayout(glayout)

    def show(self):
        self.resize(500, 300)
        super().show()

