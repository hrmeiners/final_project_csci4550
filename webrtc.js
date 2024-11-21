const socket = io();
const localVideo = document.getElementById('localVideo');
const remoteVideosContainer = document.querySelector('.remote-videos');
const videoToggleBtn = document.getElementById('video-toggle-btn');

const username = '{{ username }}';
const roomCode = '{{ code }}';

let localStream = null;
const peerConnections = {};

// WebRTC Configuration
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { 
            urls: 'turn:openrelay.metered.ca:80',
            username: 'openrelayproject',
            credential: 'openrelayproject'
        }
    ]
};

// Function to create a peer connection
async function createPeerConnection(otherUsername) {
    const peerConnection = new RTCPeerConnection(configuration);

    // Add local stream to peer connection
    if (localStream) {
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });
    }

    // Handle incoming tracks (remote video)
    peerConnection.ontrack = (event) => {
        const remoteVideo = document.createElement('video');
        remoteVideo.srcObject = event.streams[0];
        remoteVideo.autoplay = true;
        remoteVideo.playsinline = true;
        remoteVideo.classList.add('remote-video');
        remoteVideo.setAttribute('data-username', otherUsername);
        remoteVideosContainer.appendChild(remoteVideo);
    };

    // ICE candidate handling
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('webrtc_signal', {
                type: 'ice-candidate',
                signal: event.candidate,
                username: otherUsername
            });
        }
    };

    return peerConnection;
}

// Start local video
async function startLocalVideo() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ 
            video: true, 
            audio: true 
        });
        localVideo.srcObject = localStream;
    } catch (error) {
        console.error('Error accessing media devices:', error);
        alert('Could not access webcam and microphone');
    }
}

// Toggle local video on/off
videoToggleBtn.addEventListener('click', () => {
    if (localStream) {
        const videoTracks = localStream.getVideoTracks();
        videoTracks.forEach(track => {
            track.enabled = !track.enabled;
        });
        videoToggleBtn.textContent = videoTracks[0].enabled ? 
            'Disable Video' : 'Enable Video';
    }
});

// Initiate WebRTC connection with another peer
async function initializeConnection(otherUsername) {
    if (peerConnections[otherUsername]) return;

    const peerConnection = await createPeerConnection(otherUsername);
    peerConnections[otherUsername] = peerConnection;

    // Create offer
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    // Send offer to the other peer
    socket.emit('webrtc_signal', {
        type: 'offer',
        signal: offer,
        username: otherUsername
    });
}

// WebSocket Signal Handling
socket.on('webrtc_signal', async (data) => {
    try {
        const { sender, signal, type } = data;
        
        // Ignore signals from self
        if (sender === username) return;

        let peerConnection = peerConnections[sender];

        switch (type) {
            case 'offer':
                // If no existing connection, create one
                if (!peerConnection) {
                    peerConnection = await createPeerConnection(sender);
                    peerConnections[sender] = peerConnection;
                }

                // Set remote description
                await peerConnection.setRemoteDescription(
                    new RTCSessionDescription(signal)
                );

                // Create and send answer
                const answer = await peerConnection.createAnswer();
                await peerConnection.setLocalDescription(answer);

                socket.emit('webrtc_signal', {
                    type: 'answer',
                    signal: answer,
                    username: sender
                });
                break;

            case 'answer':
                // Set remote description for existing connection
                if (peerConnection) {
                    await peerConnection.setRemoteDescription(
                        new RTCSessionDescription(signal)
                    );
                }
                break;

            case 'ice-candidate':
                // Add ICE candidates
                if (peerConnection) {
                    await peerConnection.addIceCandidate(
                        new RTCIceCandidate(signal)
                    );
                }
                break;
        }
    } catch (error) {
        console.error('WebRTC signaling error:', error);
    }
});

// Initial setup
document.addEventListener('DOMContentLoaded', async () => {
    await startLocalVideo();

    // When a new user joins, automatically initiate connection
    socket.on('new user', (otherUsername) => {
        if (otherUsername !== username) {
            initializeConnection(otherUsername);
        }
    });
});

// Chat message handling (keeping existing chat functionality)
const messageInput = document.getElementById('message');
const sendBtn = document.getElementById('send-btn');

sendBtn.addEventListener('click', () => {
    const messageText = messageInput.value.trim();
    if (messageText) {
        socket.emit('message', { data: messageText });
        messageInput.value = '';
    }
});

socket.on('message', (data) => {
    const messagesContainer = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('text');
    messageElement.textContent = `${data.name}: ${data.message}`;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
});