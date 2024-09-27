import socket
import threading

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5

def main():
    # AF_INET = IPv4
    # SOCK_STREAM = TCP Connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind server to specific address/port on machine
    try:
        server.bind((HOST, PORT))
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")

    # set server limit
    server.listen(LISTENER_LIMIT)
    
    # This loop keeps listening to all client connections
    while 1:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")


if __name__ == '__main__':
    main()