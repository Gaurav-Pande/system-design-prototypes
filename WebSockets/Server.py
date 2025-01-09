## Basic websocket server
import socket
import threading
import base64
import hashlib


class WebSocketServer:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        print(f"Server started at {host}:{port}")

    def start(self):
        while True:
            # wait for an incoming connection and return a new socket for the connection
            client, address = self.socket.accept()
            print(f"Connection from {address}")
            # Start a new thread to handle the client
            threading.Thread(target=self.handle_client, args=(client,)).start()


    def handle_client(self, client):
        # websocket handshake process, similar to HTTP
        # in http handshake, the client sends a request to the server
        # the server sends a response back to the client
        # in handshake, the format of protocol is GET /path HTTP/1.1 \r\n   
        request = client.recv(1024).decode('utf-8')
        headers = self.parse_headers(request)  
        # get the websocket key from the headers
        # we can define our own key name- Websocket-Key
        websocketKey = headers['WebSocket-Key'] 
        acceptKey = self.generate_accept_key(websocketKey)
        # send the response back to the client
        response = self.handshake_response(acceptKey)
        client.send(response.encode('utf-8'))

        # start the message exchange
        while True:
            data = client.recv(1024)
            print(f"Received: {data.decode('utf-8')}")
            if data == b'exit':
                break
            client.send(data)
    
    def parse_headers(self, request):
        headers = {}
        print(f"Request received: {request}")
        lines = request.split('\r\n')
        for line in lines[1:]:
            if line:
                key, value = line.split(': ')
                headers[key] = value
        return headers
    
    def generate_accept_key(self, key):
        # magic string defined in the websocket protocol
        MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        # concatenate the key and the magic string
        key += MAGIC_STRING
        # generate the sha1 hash of the key
        key = hashlib.sha1(key.encode('utf-8')).digest()
        # return the base64 encoded hash
        return base64.b64encode(key).decode('utf-8')

    def handshake_response(self, acceptKey):
        response = "HTTP/1.1 101 Switching Protocols\r\n"
        response += "Upgrade: websocket\r\n"
        response += "Connection: Upgrade\r\n"
        response += f"Sec-WebSocket-Accept: {acceptKey}\r\n\r\n"
        return response





def main():
    server = WebSocketServer('localhost', 3000)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    # exit the server on keyboard interrupt
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping server")
        server.socket.close()

if __name__ == "__main__":
    main()
