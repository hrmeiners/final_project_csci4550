# old server imports
import socket
import threading 

# new server imports
from datetime import datetime, timezone
from typing import List, Tuple
from uuid import uuid4

from nicegui import ui



HOST = '127.0.0.1'
PORT = 1234         
LISTENER_LIMIT = 5  # max people allowed on server at once
active_clients = [] # List of all currently connected users

# List[Message[user_id, avatar, text, stamp]]
message_history: List[Tuple[str, str, str, str]] = []


# Function to send message to a single client
def send_message_to_client(client_socket, message):
    message = ui.chat_message(text=message, stamp=datetime.now(timezone.utc).strftime('%X'))
    message_history.append(message)
    client_socket.sendall(message.encode())


# Function to send any new message to all the clients that
# are currently connected to this server
def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)


# Function to listen for upcoming messages from a client
def listen_for_messages(client_socket):
    # infinitely loops and checks for incoming client messages
    while True:
        message = client_socket.recv(2048).decode('utf-8')
        
        if message != '':
            print(f"{message}")
        else:
            print(f"The message send from client is empty")





# Main function
def main():
    # Creating the socket class object
    # AF_INET: we are going to use IPv4 addresses
    # SOCK_STREAM: we are using TCP packets for communication
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # bind server to address: host, port
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")

    # Set server limit of how many clients at once
    server.listen(LISTENER_LIMIT)
    print(f"Listener Limit: {LISTENER_LIMIT}")

    # This while loop will keep listening to client connections
    while True:
        client_socket, address = server.accept()
        print(f"Successfully connected to client: address {address[0]}, port {address[1]}")
        listen_for_messages(client_socket)

if __name__ == '__main__':
    main()