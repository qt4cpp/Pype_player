import mimetypes
import os
import qtawesome
from PySide2.QtCore import QByteArray, QIODevice, QTextStream, QUrl, QTime
from PySide2.QtWidgets import QAction, QPushButton, QMessageBox


def createAction(obj, name, function, shortcut=''):
    newAction = QAction(name, obj)
    newAction.setShortcut(shortcut)
    newAction.triggered.connect(function)

    return newAction


def create_flat_button(icon, label=''):
    button = QPushButton(icon, label)
    button.setFlat(True)
    button.setFixedSize(30, 30)
    return button


def make_button_from_fa(icon_str, str='', tooltip=''):
    icon = qtawesome.icon(icon_str)
    button = QPushButton(icon, str)
    button.setToolTip(tooltip)

    return button


def ms_to_qtime(ms):
    sec = int(ms / 1000)
    h = int(sec / 3600)
    m = int((sec % 3600) / 60)
    s = int((sec % 60))
    ms = int(ms % 1000)
    return QTime(h, m, s, ms)


def qtime_to_ms(qtime: QTime) -> int:
    """
    exchange milliseconds from QTime type.
    """
    ms = (qtime.hour() * 3600) + (qtime.minute() * 60) + qtime.second()
    ms *= 1000  # msec 用に1000倍する
    ms += qtime.msec()
    return ms


def dialog_for_message(message, button=QMessageBox.Ok):
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.setStandardButtons(button)
    return msg_box

def convert_to_bytearray(urls: [QUrl], delimiter='\n') -> QByteArray:
    """modelの項目をbyte型に変換する。

    :param urls: 要素を変換するindexのリスト
    :param delimiter: データの区切り文字
    :return: byte型に変換した項目
    元に戻すための区切り文字としてself.url_delimiterプロパティを使用
    """
    urls_byte = QByteArray()
    stream = QTextStream(urls_byte, QIODevice.WriteOnly)
    for url in urls:
        stream << url.toString() << delimiter
    return urls_byte


def convert_from_bytearray(byte_array: QByteArray, delimiter='\n') -> [QUrl]:
    """渡されたbyte arrayから元のデータに復元する。

    :param byte_array:
    :param delimiter: データの区切り文字
    :return:
    区切り文字はself.url_delimiterプロパティ
    """
    byte_list = byte_array.split(delimiter)
    urls = []
    for data in byte_list:
        url = QUrl(data.data().decode('utf-8'))
        urls.append(url)
    return urls

def get_mime_type(file_path):
    """渡されたファイルのMIME type を返す。"""
    if os.path.isfile(file_path):
        return mimetypes.guess_type(file_path)[0]
    else:
        print('Error (get_mime_type):', file_path)
        return None

def is_media(file_path):
    """video/audio であればTrueを返す"""
    return is_video(file_path) | is_audio(file_path)

def is_video(file_path):
    """videoファイルであればTrueを返す"""
    if os.path.isfile(file_path):
        mime = get_mime_type(file_path)
        if mime and 'video' in mime:
            return True
    return False

def is_audio(file_path):
    """audio ファイルであればTrueを返す"""
    if os.path.isfile(file_path):
        mime = get_mime_type(file_path)
        if mime and 'audio' in mime:
            return True
    return False
