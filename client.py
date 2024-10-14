import socket
import threading

HOST = '127.0.0.1'
PORT = 1234

# Creating a socket object
# AF_INET: we are using IPv4 
# SOCK_STREAM: we are using TCP 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# add message to the UI window
# def add_message(message):
    

def connect():
    # connect to server
    try:
        server_socket.connect((HOST, PORT))
        print("Successfully connected to server")
        # add_message("[SERVER] Successfully connected to the server")
    except:
        print("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")

    print("Please type your username:")
    username = input()

    while username == '':    
        print("Invalid username: Username cannot be empty")
        print("Please retype your username:")
        username = input()
        
    server_socket.sendall(username.encode())
    listen_for_messages_from_server(server_socket)
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
    
    
    

'''
root = tk.Tk()
root.geometry("600x600")
root.title("Messenger Client")
root.resizable(False, False)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

top_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=600, height=400, bg=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

username_label = tk.Label(top_frame, text="Enter username:", font=FONT, bg=DARK_GREY, fg=WHITE)
username_label.pack(side=tk.LEFT, padx=10)

username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=23)
username_textbox.pack(side=tk.LEFT)

username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=connect)
username_button.pack(side=tk.LEFT, padx=15)

message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=38)
message_textbox.pack(side=tk.LEFT, padx=10)

message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=send_message)
message_button.pack(side=tk.LEFT, padx=10)

message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE, width=67, height=26.5)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP)
'''