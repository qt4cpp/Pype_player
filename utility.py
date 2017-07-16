import qtawesome
from PyQt5.QtCore import QByteArray, QIODevice, QTextStream, QUrl
from PyQt5.QtWidgets import QAction, QPushButton


def createAction(obj, name, function, shortcut=''):
    newAction = QAction(name, obj)
    newAction.setShortcut(shortcut)
    newAction.triggered.connect(function)

    return newAction

def make_button_from_fa(icon_str, str=''):
    icon = qtawesome.icon(icon_str)
    button = QPushButton(icon, str)

    return button


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

