import socket
import ssl
import threading
import os

class ChatServer:
    def __init__(self, host, port, certfile, keyfile):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.clients = []
        self.server_socket = None

    def start_server(self):
        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)  # Set the backlog to 5

            print(f"Server listening on {self.host}:{self.port}...")

            while True:
                client_socket, client_address = self.server_socket.accept()
                secure_socket = context.wrap_socket(client_socket, server_side=True)
                self.clients.append(secure_socket)

                # Start a new thread to handle each client
                threading.Thread(target=self.handle_client, args=(secure_socket,)).start()
                
                # Print message when a new client connects
                print(f"Client connected: {client_address}")
        except Exception as e:
            print(f"Error starting server: {e}")

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Check if the message is a file
                if data.startswith(b"FILE:"):
                    # Extract filename and file data
                    filename, file_data = data.split(b"\n", 1)
                    filename = filename.decode().split(":")[-1].strip()
                    
                    # Save the file
                    with open(filename, 'wb') as file:
                        file.write(file_data)
                    
                    # Broadcast file message to all clients
                    for client in self.clients:
                        if client != client_socket:
                            client.send(f"{filename} received".encode())
                else:
                    # Broadcast message to all clients
                    for client in self.clients:
                        if client != client_socket:
                            client.send(data)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Remove client from the list
            self.clients.remove(client_socket)
            client_socket.close()

if __name__ == "__main__":
    server = ChatServer('0.0.0.0', 12000,'C:/Program Files/OpenSSL-Win64/bin/server.crt', 'C:/Program Files/OpenSSL-Win64/bin/server.key')
    server.start_server()
