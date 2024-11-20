
class VideoChat {
    constructor(roomId, socketio) {
      this.roomId = roomId;
      this.socket = socketio;
      this.peerConnections = {};
      this.localStream = null;
      this.configuration = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      };
      
      this.setupSocketListeners();
    }
  
    async initializeVideo() {
      try {
        this.localStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
          },
          audio: true
        });
        
        const localVideo = document.getElementById('localVideo');
        localVideo.srcObject = this.localStream;
        
        this.socket.emit('join_video_room', {
          roomId: this.roomId
        });
      } catch (err) {
        console.error('Error accessing media devices:', err);
      }
    }
  
    async createPeerConnection(userId) {
      const peerConnection = new RTCPeerConnection(this.configuration);
      
      // Add local tracks to the connection
      this.localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, this.localStream);
      });
  
      // Handle ICE candidates
      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          this.socket.emit('ice_candidate', {
            candidate: event.candidate,
            to: userId
          });
        }
      };
  
      // Handle incoming tracks
      peerConnection.ontrack = (event) => {
        const remoteVideo = document.getElementById(`remoteVideo-${userId}`);
        if (!remoteVideo) {
          this.createRemoteVideoElement(userId);
        }
        remoteVideo.srcObject = event.streams[0];
      };
  
      this.peerConnections[userId] = peerConnection;
      return peerConnection;
    }
  
    createRemoteVideoElement(userId) {
      const videoGrid = document.getElementById('videoGrid');
      const videoElement = document.createElement('video');
      videoElement.id = `remoteVideo-${userId}`;
      videoElement.autoplay = true;
      videoElement.playsInline = true;
      videoGrid.appendChild(videoElement);
    }
  
    setupSocketListeners() {
      // Handle new user joining
      this.socket.on('user_joined_video', async (data) => {
        const peerConnection = await this.createPeerConnection(data.userId);
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        this.socket.emit('video_offer', {
          offer: peerConnection.localDescription,
          to: data.userId
        });
      });
  
      // Handle incoming video offers
      this.socket.on('video_offer', async (data) => {
        const peerConnection = await this.createPeerConnection(data.from);
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
        
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        
        this.socket.emit('video_answer', {
          answer: peerConnection.localDescription,
          to: data.from
        });
      });
  
      // Handle video answers
      this.socket.on('video_answer', async (data) => {
        const peerConnection = this.peerConnections[data.from];
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
      });
  
      // Handle ICE candidates
      this.socket.on('ice_candidate', async (data) => {
        const peerConnection = this.peerConnections[data.from];
        await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
      });
  
      // Handle user disconnect
      this.socket.on('user_left_video', (data) => {
        if (this.peerConnections[data.userId]) {
          this.peerConnections[data.userId].close();
          delete this.peerConnections[data.userId];
        }
        
        const remoteVideo = document.getElementById(`remoteVideo-${data.userId}`);
        if (remoteVideo) {
          remoteVideo.remove();
        }
      });
    }
  }
  
  // Export for use in other files
  export default VideoChat;