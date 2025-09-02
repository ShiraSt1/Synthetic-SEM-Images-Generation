import sys, os, json, base64
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QWidget,
    QVBoxLayout, QHBoxLayout, QScrollArea, QSizePolicy, QMessageBox
)
    # Make sure you have QMessageBox/QScrollArea in the import if not already included
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5.QtNetwork import QTcpSocket

class MainWindow(QMainWindow):
    """
    Sends text to a server via TCP, receives JSON with images_base64,
    and displays the images on screen (without saving them to files).
    """

    def __init__(self):
        super().__init__()

        # ----- TCP -----
        server_host = os.getenv("SERVER_HOST", "localhost")
        server_port = int(os.getenv("SERVER_PORT", "12345"))

        self.socket = QTcpSocket()
        self.socket.connectToHost(server_host, server_port)
        self.socket.waitForConnected(3000)
        self.socket.errorOccurred.connect(self._on_socket_error)
        self.socket.readyRead.connect(self.on_ready_read)  # <<< New: listening for server response

        # Buffer for partial messages until '\n' arrives from the server
        self._rx_buf = b""

        # ----- UI -----
        self.setWindowTitle("Text → Image (display)")
        self.resize(1000, 700)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self.label = QLabel("Type any text you want, and it will turn into a picture:")
        self.text_edit = QTextEdit()
        self.button = QPushButton("Create Image")
        self.button.clicked.connect(self.on_click)

        # Scrollable display area for images
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.images_container = QWidget()
        self.images_layout = QHBoxLayout(self.images_container)
        self.images_layout.setContentsMargins(8, 8, 8, 8)
        self.images_layout.setSpacing(12)
        self.scroll.setWidget(self.images_container)

        root.addWidget(self.label)
        root.addWidget(self.text_edit, stretch=0)
        root.addWidget(self.button, stretch=0)
        root.addWidget(self.scroll, stretch=1)

        # Small status bar at the bottom
        self.status = QLabel("")
        self.status.setStyleSheet("color: #666;")
        root.addWidget(self.status)

    # ---------- UI Actions ----------

    def on_click(self) -> None:
        txt = self.text_edit.toPlainText().strip()
        if not txt:
            QMessageBox.information(self, "Empty", "Please type some text 🙂")
            return
        # Send text to server
        self.button.setEnabled(False)
        self.status.setText("Generating…")
        self._clear_images()

        self.socket.write(txt.encode("utf-8"))
        self.text_edit.clear()

    def _on_socket_error(self, e):
        QMessageBox.critical(self, "Socket error", f"Socket error: {e}")
        self.button.setEnabled(True)
        self.status.setText("")

    # ---------- Networking ----------

    def on_ready_read(self):
        """
        Reads from the socket until a newline is reached, decodes JSON,
        and displays images.
        The server terminates each response with '\n',
        which indicates the end of a message.
        """
        self._rx_buf += bytes(self.socket.readAll())
        if b"\n" not in self._rx_buf:
            return  # Wait for full message

        parts = self._rx_buf.split(b"\n")
        complete_msgs = parts[:-1]
        self._rx_buf = parts[-1]  # Keep remainder for next read

        for raw in complete_msgs:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            if line.startswith("LLM_ERROR"):
                self._show_error_text(line)
                continue

            try:
                data = json.loads(line)
            except Exception as ex:
                self._show_error_text(f"Response is not JSON:\n{line}\n\n{ex}")
                continue

            imgs = data.get("images_base64") or []
            if not isinstance(imgs, list) or not imgs:
                self._show_error_text(f"No images in response:\n{data}")
                continue

            self._display_images(imgs)

        self.button.setEnabled(True)
        self.status.setText("")

    # ---------- Image Display ----------

    def _clear_images(self):
        while self.images_layout.count():
            item = self.images_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _display_images(self, b64_list):
        for b64img in b64_list:
            try:
                img_bytes = base64.b64decode(b64img)
                qimg = QImage.fromData(img_bytes)
                if qimg.isNull():
                    raise ValueError("QImage is null")

                pm = QPixmap.fromImage(qimg)

                # If the image is too wide — resize it proportionally
                max_w = 420
                if pm.width() > max_w:
                    pm = pm.scaledToWidth(max_w, Qt.SmoothTransformation)

                lbl = QLabel()
                lbl.setPixmap(pm)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
                lbl.setStyleSheet("border:1px solid #ddd; padding:6px; background:#fff;")
                self.images_layout.addWidget(lbl)
            except Exception as ex:
                self._show_error_text(f"Failed to decode image: {ex}")

        # Add spacer at the end
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.images_layout.addWidget(spacer)

    def _show_error_text(self, msg: str):
        self.status.setText("Error")
        QMessageBox.warning(self, "Error", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())