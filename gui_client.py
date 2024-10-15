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
        # add_message("[SERVER] Successfully connected to the server")
    except:
        print("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")


# Function to send message to the server
def send_message_to_server(message):
    server_socket.sendall(message[2].encode())



#!/usr/bin/env python3
from datetime import datetime, timezone
from typing import List, Tuple
from uuid import uuid4

from nicegui import ui

# List[Message[user_id, avatar, text, stamp]]
messages: List[Tuple[str, str, str, str]] = []



@ui.refreshable
def chat_messages(own_id: str) -> None:
    if messages:
        for user_id, avatar, text, stamp in messages:
            ui.chat_message(text=text, name=user_id, avatar=avatar, stamp=stamp, sent=own_id == user_id)
            print(f"UI chat message: {text}")
            
    else:
        ui.label('No messages yet').classes('mx-auto my-36')
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')


@ui.page('/')
async def main():
    def send() -> None:
        # STAMP IS OUTPUTTING INCORRECT TIME
        stamp = datetime.now(timezone.utc).strftime('%X')
        messages.append((user_id, avatar, text.value, stamp))
        text.value = ''
        chat_messages.refresh()
        send_message_to_server(messages[-1])

    user_id = str(uuid4())
    avatar = f'https://robohash.org/{user_id}?bgset=bg2'

    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')
    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            with ui.avatar().on('click', lambda: ui.navigate.to(main)):
                ui.image(avatar)
            text = ui.input(placeholder='message').on('keydown.enter', send) \
                .props('rounded outlined input-class=mx-3').classes('flex-grow')
        ui.markdown('GUI implemented with[NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')

    await ui.context.client.connected()  # chat_messages(...) uses run_javascript which is only possible after connecting
    with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
        chat_messages(user_id)




if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
    connect()
    
    