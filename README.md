# SemTTI

A simple client-server demo application using **PyQt5** and **TCP sockets**.  
The project demonstrates sending text from a GUI client to a TCP server, which receives and prints the messages.  
It can serve as a foundation for more advanced applications such as text-to-image systems, chat apps, or other socket-based communication tools.

---

## Features
- **GUI Client (PyQt5)** – User-friendly interface with text input and a button.  
- **TCP Communication** – Client connects to a server via TCP on port `12345`.  
- **Server** – Listens for incoming client connections and prints received text.  
- **Extensible** – Easy to extend for more complex protocols or additional functionality.  

---

## Project Structure
The project contains the following files:
- **client.py** – The graphical client application. 
Opens a PyQt5 window where the user can type text and send it to the server.  
- **server.py** – The TCP server. Listens on port `12345`, 
receives text from clients, and prints it to the console.  
- **README.md** – This documentation file. 
Explains installation, usage, and project details.  