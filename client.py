import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpSocket

"""
PyQt5 client GUI that connects to a TCP server (localhost:12345).
User enters text and sends it to the server with a button click.
"""

class MainWindow(QMainWindow):
   """
    Main window for the client.
    Connects to the server, shows a text box and button,
    and sends user input to the server.
    """
   
   def __init__(self):
      """Set up window, UI elements, and TCP connection."""
      super().__init__()

      # TCP socket connection
      self.socket = QTcpSocket()
      self.socket.connectToHost("localhost", 12345)

      # Window setup
      self.setWindowTitle("Text 2 Image")
      self.resize(800, 600)

      # Central widget + vertical layout.
      central = QWidget(self)
      self.setCentralWidget(central)
      layout = QVBoxLayout(central)

      # UI controls.
      self.label = QLabel("Type any text you want, and it will turn into a picture:")
      self.text_edit = QTextEdit()
      self.button = QPushButton("Create Image")

      # Button action
      def on_click() -> None:
         """Send current text to the server."""
         text = self.text_edit.toPlainText()
         self.socket.write(text.encode())

      self.button.clicked.connect(on_click)

      # Add controls to the layout in top-to-bottom order.
      layout.addWidget(self.label)
      layout.addWidget(self.text_edit)
      layout.addWidget(self.button)

if __name__ == "__main__":
    # Create the Qt application and show the main window.
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

     # Start the Qt event loop.
    sys.exit(app.exec_())