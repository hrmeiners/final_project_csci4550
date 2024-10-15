import socket
import threading

HOST = '127.0.0.1'
PORT = 1234

# Creating a socket object
# AF_INET: we are using IPv4 
# SOCK_STREAM: we are using TCP 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

def connect():
    # connect to server
    try:
        server_socket.connect((HOST, PORT))
        print("Successfully connected to server")
    except:
        print("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")

    print("Please type your username:")
    username = input()

    while username == '':    
        print("Invalid username: Username cannot be empty")
        print("Please retype your username:")
        username = input()
        
    server_socket.sendall(username.encode())
    # listen_for_messages_from_server(server_socket)
    # threading.Thread(target=listen_for_messages_from_server, args=(server, )).start()


def send_message():
    message = input()
    while message == '':
        print("Empty message", "Message cannot be empty")
        message = input()

    server_socket.sendall(message.encode())


def listen_for_messages_from_server(server):
    # infinitely loops
    while True:
        message = server.recv(2048).decode('utf-8')
        if message != '':
            username = message.split("~")[0]
            content = message.split('~')[1]

            # add_message(f"[{username}] {content}")
        else:
            print("Error", "Message recevied from server is empty")


# main function
def main():
    connect()    
    
if __name__ == '__main__':
    main()
    
    