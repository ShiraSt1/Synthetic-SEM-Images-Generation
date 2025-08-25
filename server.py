from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress

app = QCoreApplication([])

server = QTcpServer()
server.listen(QHostAddress.Any, 12345)

def on_new_connection():
    client = server.nextPendingConnection()
    client.readyRead.connect(lambda: print(client.readAll().data().decode("utf-8")))

server.newConnection.connect(on_new_connection)

print("Server running on port 12345")
app.exec_()
