"""
Minimal TCP→LLM relay.

Flow:
  TCP client text → handle_ready_read() → llm.chat_text(text) → write reply.
The LLM client is created once via factory+ENV (see llm/factory.py and .env).
"""
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress
from dotenv import load_dotenv
import sys

from llm.factory import create_llm  

load_dotenv()

app = QCoreApplication([])
server = QTcpServer()

# Start listening on 0.0.0.0:12345
if not server.listen(QHostAddress.Any, 12345):
    print("Listen failed")
    sys.exit(1)

# Create one LLM client (adapter) for the entire process.
# The factory reads: LLM_PROVIDER, LLM_BASE_URL, LLM_MODEL, LLM_API_KEY, LLM_TIMEOUT.
llm = create_llm()

def handle_ready_read(client):
    """Read bytes from the socket, call the LLM, write back the text reply."""
    data_bytes = client.readAll().data()
    if not data_bytes:
        return
    text = data_bytes.decode("utf-8", errors="replace").strip()
    print(f"[TCP IN] {text}")

    try:
        reply = llm.chat_text(text, max_tokens=500)
        print(f"[LLM OUT] {reply.text}")

        # Many TCP clients expect a newline to detect end-of-message.
        wire = (reply.text + "\n").encode("utf-8", errors="replace")
        client.write(wire)
        client.flush()  # ensure it goes out immediately
        # Optional for simple clients: close after one reply
        # client.disconnectFromHost()
    except Exception as e:
        err = f"LLM_ERROR: {e}"
        print(err)
        client.write(err.encode("utf-8"))

def on_new_connection():
    """Wire per-connection signals to our handler and cleanup."""
    client = server.nextPendingConnection()
    print("[TCP] new connection")
    client.readyRead.connect(lambda: handle_ready_read(client))
    client.disconnected.connect(lambda: print("[TCP] disconnected"))
    client.disconnected.connect(client.deleteLater)

server.newConnection.connect(on_new_connection)
print("Server running on port 12345")
app.exec_()
