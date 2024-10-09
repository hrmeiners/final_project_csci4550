import socket
import threading

host = '127.0.0.1'
port = 1234
max_limit = 3
active_clients = []


def listen_for_messages
# Sending any new messages to all clients that are connected to server
def send_messages_to_all(from_username, message):
    pass
# Handling Client
def client_handler(client):
    # The server will listen for client messages that will contain the username
    while 1:
        username = client.recv(2048).decode('utf-8')
        if username != '':
            active_clients.append((username, client))
        else:
            print("Client username is blank!")
def main():
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # using IPv4 addresses and TCP packets

    try:
        # Host IP and Port
        server.bind((host,port))
    except:
        print("Binding to the host was unsuccessful!")

    # Set a server limit
    server.listen(max_limit)

    while 1:

        client, address = server.accept()
        print("Connecting to client was successful!")

        threading.Thread(target=client_handler,args = client(client,)).start()
if __name__ == "__main__":
    main()