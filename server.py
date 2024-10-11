import socket
import threading

HOST = '127.0.0.1'
PORT = 1234         
LISTENER_LIMIT = 5  # max people allowed on server at once
active_clients = [] # List of all currently connected users


# Function to listen for upcoming messages from a client
def listen_for_messages(client, username):
    # infinitely loops and checks for incoming client messages
    while 1:
        message = client.recv(2048).decode('utf-8')
        
        if message != '':
            final_msg = username + '~' + message
            send_messages_to_all(final_msg)
        else:
            print(f"The message send from client {username} is empty")


# Function to send message to a single client
def send_message_to_client(client, message):
    client.sendall(message.encode())


# Function to send any new message to all the clients that
# are currently connected to this server
def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)


# Function to handle client
def client_handler(client):
    # infinitely loops
    while 1:
        username = client.recv(2048).decode('utf-8')
        
        # add new user to active_clients
        if username != '':
            active_clients.append((username, client))
            prompt_message = "SERVER~" + f"{username} added to the chat"
            send_messages_to_all(prompt_message)
            break
        else:
            print("Client username is empty")

    threading.Thread(target=listen_for_messages, args=(client, username, )).start()


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

    # This while loop will keep listening to client connections
    while 1:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")

        threading.Thread(target=client_handler, args=(client, )).start()



if __name__ == '__main__':
    main()