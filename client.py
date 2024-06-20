import tkinter as tk
from tkinter import ttk, filedialog
import socket
import ssl
import threading
import sys

class ChatClientGUI:
    def __init__(self, host, port, certfile):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.client_socket = None
        self.username = None

        self.root = tk.Tk()
        self.root.title("Chat Client")

        self.username_label = ttk.Label(self.root, text="Enter your username:")
        self.username_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.username_entry = ttk.Entry(self.root, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.connect_button = ttk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=2, padx=5, pady=5)

        self.file_button = ttk.Button(self.root, text="Send File", command=self.send_file)
        self.file_button.grid(row=0, column=3, padx=5, pady=5)

        self.exit_button = ttk.Button(self.root, text="Exit", command=self.exit_client)
        self.exit_button.grid(row=0, column=4, padx=5, pady=5)

        self.chat_frame = ttk.Frame(self.root, padding="10")
        self.chat_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        self.chat_text = tk.Text(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 12))
        self.chat_text.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient=tk.VERTICAL, command=self.chat_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.config(yscrollcommand=self.scrollbar.set)

        self.input_frame = ttk.Frame(self.root, padding="10")
        self.input_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

        self.message_entry = ttk.Entry(self.input_frame, width=50, font=("Helvetica", 12))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

    def connect_to_server(self):
        try:
            self.username = self.username_entry.get()
            if not self.username:
                print("Please enter a username.")
                return

            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(cafile=self.certfile)

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            # Wrap the socket with SSL
            self.client_socket = context.wrap_socket(self.client_socket, server_hostname=self.host)

            # Send the username to the server for authentication
            self.client_socket.send(self.username.encode())
            
            # Send a join message to the server
            join_message = f"{self.username} has joined the chatroom."
            self.client_socket.send(join_message.encode())
  

            # Start a new thread to handle receiving messages
            threading.Thread(target=self.receive_messages).start()

            # Print message when connected to the server
            self.print_message(f"Connected to {self.host}:{self.port}")

            # Disable username entry after connection
            self.username_entry.config(state=tk.DISABLED)
            self.connect_button.config(state=tk.DISABLED)

        except Exception as e:
            print(f"Error connecting to server: {e}")

    def send_message(self):
        try:
            message = self.message_entry.get()
            if self.client_socket:
                self.print_message(f"You: {message}")
                full_message = f"{self.username}: {message}"
                self.client_socket.send(full_message.encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            else:
                print("Socket connection not initialized or closed.")
        except Exception as e:
            print(f"Error sending message: {e}")

    def send_file(self):
        try:
            file_path = filedialog.askopenfilename()
            if file_path:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    filename = file_path.split('/')[-1]  # Extract filename from path

                # Prefix the message to distinguish it as a file
                full_message = f"FILE: {self.username}: {filename}\n".encode() + file_data
                self.client_socket.send(full_message)
		
        except Exception as e:
            print(f"Error sending file: {e}")

    def receive_messages(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                # Check if the message is a file message
                if data.startswith(b"FILE:"):
                    # Extract the filename and the sender's username from the message
                    _, sender_username, filename = data.decode().split(":", 2)

                    # Display a message in the chat box indicating the received file
                    self.print_message(f"Received file from {sender_username}: {filename.strip()}")

                    # Save the file
                    file_data = data.split(b"\n", 1)[1]
                    with open(filename.strip(), "wb") as file:
                        file.write(file_data)
                else:
                    # Display the received data in the chat box
                    self.chat_text.config(state=tk.NORMAL)
                    self.chat_text.insert(tk.END, f"{data.decode('utf-8')}\n")
                    self.chat_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error receiving messages: {e}")

    def print_message(self, message):
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{message}\n")
        self.chat_text.config(state=tk.DISABLED)
    
    def exit_client(self):
        try:
            if self.client_socket:
                self.client_socket.close()  # Close the client socket
            sys.exit()  # Exit the application
        except Exception as e:
            print(f"Error exiting client: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client_gui = ChatClientGUI('192.168.56.1', 12000, 'certificate.crt')
    client_gui.run()
