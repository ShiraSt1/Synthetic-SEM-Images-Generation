from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress
from dotenv import load_dotenv
import requests, sys, json
import os

FORWARD_URL = "https://cable-innovative-launches-aspect.trycloudflare.com/v1/chat/completions"
load_dotenv()
API_KEY = os.getenv("API_KEY") 

app = QCoreApplication([])

server = QTcpServer()
ok = server.listen(QHostAddress.Any, 12345)
if not ok:
    print("Listen failed")
    sys.exit(1)

def call_llama(prompt_text: str) -> str:
    r = requests.post(
        FORWARD_URL,
        json={
            "model": "local-llama",
            "messages": [{"role": "user", "content": prompt_text}],
            "max_tokens": 1000,
        },
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    # החזרת הטקסט של המודל (אפשר גם להחזיר את כל ה־JSON אם תרצי)
    return data["choices"][0]["message"]["content"]

def handle_ready_read(client):
    data_bytes = client.readAll().data()
    if not data_bytes:
        return
    text = data_bytes.decode("utf-8", errors="replace").strip()
    print(f"[TCP IN] {text}")

    try:
        reply = call_llama(text)
        print(f"[LLM OUT] {reply}")
        client.write(reply.encode("utf-8"))
    except Exception as e:
        err = f"HTTP_FORWARD_ERROR: {e}"
        print(err)
        client.write(err.encode("utf-8"))
    # finally:
    #     client.flush()
    #     client.disconnectFromHost()  # סוגר חיבור אחרי תגובה (פשוט לבדיקות)

def on_new_connection():
    client = server.nextPendingConnection()
    print("[TCP] new connection")
    client.readyRead.connect(lambda: handle_ready_read(client))
    client.disconnected.connect(lambda: print("[TCP] disconnected"))
    client.disconnected.connect(client.deleteLater)

server.newConnection.connect(on_new_connection)
print("Server running on port 12345")
app.exec_()
