import socket
import threading

# target host and port for server
HOST = '127.0.0.1'
PORT = 1234


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    

    # Connect to the server
    try:
        client.connect((HOST, PORT))
        print(f"Successfully connected to server")
    except:
        print(f"Unable to connect to server: {HOST} {PORT}")


if __name__ == '__main__':
    main()