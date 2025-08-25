import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpSocket

class MainWindow(QMainWindow):
   def __init__(self):
      super().__init__()

      self.socket = QTcpSocket()
      self.socket.connectToHost("localhost", 12345)

      self.setWindowTitle("Text 2 Image")
      self.resize(800, 600)
      # יצירת ה־central widget
      central = QWidget(self)
      self.setCentralWidget(central)
      # יצירת Layout (כאן Vertical)
      layout = QVBoxLayout(central)
      # יצירת רכיבים
      self.label = QLabel("Type any text you want, and it will turn into a picture:")
      self.text_edit = QTextEdit()
      self.button = QPushButton("Create Image")

      def on_click():
         text = self.text_edit.toPlainText()
         self.socket.write(text.encode())

      self.button.clicked.connect(on_click)

      # הוספה ל־layout
      layout.addWidget(self.label)
      layout.addWidget(self.text_edit)
      layout.addWidget(self.button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())