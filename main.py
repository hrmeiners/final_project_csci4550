from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for
from aiortc import RTCPeerConnection, RTCSessionDescription
from flask_socketio import join_room, leave_room, send, SocketIO
from flask_socketio import emit
import random
from string import ascii_uppercase
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Random import get_random_bytes
import base64

app = Flask(__name__)
app.config["SECRET_KEY"] = "gorilla123"
socketio = SocketIO(app)

rooms = {}

def room_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            break
    return code

def generate_rsa_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key(format='PEM')
    public_key = key.publickey().export_key(format='PEM')
    return private_key, public_key

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home_page.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home_page.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = room_code(4)
            rooms[room] = {
                "members": 0,
                "messages": [],
                "public_keys": {},  # Initialize the public_keys dictionary
                "aes_key": get_random_bytes(16)  # Set AES key for the room
            }
            print(f"Room created: {room} with AES key: {rooms[room]['aes_key']}")
        elif code not in rooms:
            return render_template("home_page.html", error="Room does not exist.", code=code, name=name)
        
        # Generate keys for the user
        private_key, public_key = generate_rsa_key_pair()
        rooms[room]["public_keys"][name] = public_key
        print(f"User {name} joined room {room} with public key: {public_key}")

        # Store session details
        session["room"] = room
        session["name"] = name
        session["private_key"] = private_key
        session["public_key"] = public_key

        return redirect(url_for("room"))

    return render_template("home_page.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    public_key = rooms[room]["public_keys"].get(session["name"])

    # Encrypt AES key with each user's public key
    aes_key = rooms[room]["aes_key"]
    print(f"Public Key: {public_key}")
    print(f"AES Key: {aes_key}")
    print(f"Original AES Key (Hex): {aes_key.hex()}")
    rsa_public_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)
    encrypted_aes_key_base64 = base64.b64encode(encrypted_aes_key).decode('UTF-8')
    private_key = session["private_key"].decode('UTF-8')
    return render_template("rooms_page.html", code=room, messages=rooms[room]["messages"], encrypted_aes_key=encrypted_aes_key_base64, private_key=private_key)

@socketio.on("message")
def message(data):
    print("Received message: ", data)
    room = session.get("room")
    if room not in rooms:
        return 
    
    encrypted_message = data["data"]
    sender_name = session.get("name")

    content = {
        "name": sender_name,
        "message": encrypted_message,
        "type": "user"
    }
    
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{sender_name} sent encrypted message: {encrypted_message}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": f"{name} has entered the room", "type": "system"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")
    
@socketio.on('disconnect')
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
        
        # Notify others about video disconnect
        emit('user_left_video', 
             {'userId': request.sid}, 
             room=room,
             skip_sid=request.sid)

    send({"name": name, "message": f"{name} has left the room", "type": "system"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
    