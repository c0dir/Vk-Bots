from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class CaptchaDialog(QDialog):

  def __init__(self, imageData):
    super().__init__(None)
    self.imageData = imageData
    self.result = None
    self.setupUi()
    self.connectSlots()

  def setupUi(self):
    self.setModal(True)
    self.setFixedSize(250, 150)
    self.setWindowTitle(self.tr('Captcha Dialog'))
    self.layout = QVBoxLayout()
    self.label = QLabel()
    self.label.setAlignment(Qt.AlignCenter)
    pix = QPixmap.fromImage(QImage.fromData(self.imageData))
    self.label.setPixmap(pix)
    self.layout.addWidget(self.label)
    self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.input = QLineEdit()
    self.input.setPlaceholderText(self.tr('Type Text from Image'))
    # self.input.setFocus(True)
    self.layout.addWidget(self.input)
    self.submit = QPushButton(self.tr('Submit'))
    self.layout.addWidget(self.submit)
    self.setLayout(self.layout)

  def connectSlots(self):
    self.input.returnPressed.connect(self.accept)
    self.submit.clicked.connect(self.accept)
    self.finished.connect(self.onfinished)

  def onfinished(self, r):
    if r == QDialog.Accepted:
      self.result = self.input.text().strip()


if __name__ == '__main__':
  import requests
  a = QApplication([])
  r = requests.get('https://api.vk.com/captcha.php?sid=656102463982&s=1')
  w = CaptchaDialog(r.content)
  if w.exec_():
    print('Input:', w.result)
