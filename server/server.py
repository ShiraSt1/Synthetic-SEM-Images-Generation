from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress

"""
Simple TCP server using PyQt5.
Listens on port 12345 and prints any text received from clients.
"""

app = QCoreApplication([])

# Create TCP server and start listening
server = QTcpServer()
ok = server.listen(QHostAddress.Any, 12345)
if not ok:
    print("Listen failed")
    
def on_new_connection():
    """Handle new client and print incoming text."""
    client = server.nextPendingConnection()
    client.readyRead.connect(lambda: print(client.readAll().data().decode("utf-8")))

# Connect the signal for new client connections
server.newConnection.connect(on_new_connection)

print("Server running on port 12345")

# Run the event loop
app.exec_()
