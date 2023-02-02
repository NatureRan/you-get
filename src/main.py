# coding:utf-8

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
    QToolTip, QMessageBox, QDesktopWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLineEdit, QLabel, QTextBrowser)
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from PyQt5.QtCore import QObject, pyqtSignal
from you_get import common
import threading

class Stream(QObject):
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

    def flush(self):
        pass

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.urlEdit = None
        self.log = None
        self.log = QTextBrowser()
        sys.stdout = Stream(newText = self.onUpdateText)
        sys.stderr = Stream(newText = self.onUpdateText)
        self.downloadThread = None
        self.initUI()

    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.log.setTextCursor(cursor)
        self.log.ensureCursorVisible()

    def initUI(self):

        # 需要设置电脑上存在的字体
        # QToolTip.setFont(QFont('SansSerif', 10))

        grid = QGridLayout()
        self.setLayout(grid)
        
        self.urlEdit = QLineEdit()
        self.urlEdit.setPlaceholderText('粘贴视频网址到此处')
        urlCheckBtn = QPushButton('检索视频', self)
        urlCheckBtn.setToolTip('This is a <b>QPushButton</b> widget')
        urlCheckBtn.resize(urlCheckBtn.sizeHint())
        urlCheckBtn.clicked.connect(self.urlCheckBtnClick)
        
        print('等待。。。')

        grid.addWidget(self.urlEdit, 0, 0)
        grid.addWidget(urlCheckBtn, 0, 1)
        grid.addWidget(self.log, 1, 0, 2, 2)

        # 设置窗口大小并居中
        self.resize(500, 300)
        self.center()
        self.setWindowTitle('网络视频下载器')
        self.setWindowIcon(QIcon('icon.jpg'))

        self.show()

    def center(self):

        qr = self.frameGeometry()
        # 获取桌面中心点坐标
        cp = QDesktopWidget().availableGeometry().center()
        # 然后把主窗口框架的中心点放置到屏幕的中心位置
        qr.moveCenter(cp)
        # 通过move函数把主窗口的左上角移动到其框架的左上角，这样就把窗口居中了
        self.move(qr.topLeft())

    def urlCheckBtnClick(self):
        if self.downloadThread is None or not self.downloadThread.isAlive():
            url = self.urlEdit.text()
            self.downloadThread = threading.Thread(target=self.download, args=(url,))
            self.downloadThread.start()

    def download(self, url):
        print('解析视频地址:' + self.urlEdit.text())
        # 将连接提交到下载API，需要设置保存路径
        common.any_download(url=url, output_dir = '/Users/nature/Downloads/', merge = True)
        print('视频下载完成')

    def closeEvent(self, event):
        if self.downloadThread is None or not self.downloadThread.isAlive():
            event.accept()
            return

        reply = QMessageBox.question(self, 'Message', 
            "存在进行中的下载，是否继续退出？", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    mainWindow = MainWindow()

    sys.exit(app.exec())
