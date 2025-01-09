# A simple class for websocket client
import socket

class WebSocketClient:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host    
        self.port = port


    def send(self, data):
        self.socket.send(data.encode('utf-8'))

    def connect(self):
        self.socket.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")
        self.handshake()
    
    def handshake(self):
        # send a handshake request to the server
        # the key is a random string encoded in base64
        key = 'dGhlIHNhbXBsZSBub25jZQ=='
        request = f"GET / HTTP/1.1\r\nHost: {self.host}:{self.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nWebSocket-Key: {key}\r\nWebSocket-Version: 13\r\n\r\n"
        self.send(request)
        response = self.socket.recv(1024).decode('utf-8')
        print(f"Handshake response: {response}")
        print("Handshake successful")

    def receive(self):
        return self.socket.recv(1024).decode('utf-8')
    
    def close(self):
        self.socket.close()
        print("Connection closed")

def main():
    # create a new websocket client
    client = WebSocketClient('localhost', 3000)
    client.connect()
    while True:
        # send a message to the server
        message = input("Enter a message: ")
        client.send(message)
        # receive a message from the server
        response = client.receive()
        print(f"Received: {response}")
        if response == 'exit':
            break
    client.close()

if __name__ == '__main__':
    main()

