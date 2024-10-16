from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread
from time import sleep

client_socket = socket(AF_INET, SOCK_STREAM)
broadcast_socket = socket(AF_INET, SOCK_DGRAM)


def connect_to_server(ip, port):
    global client_socket

    try:
        server_ip, server_port = ip, int(port)

        client_socket = socket(AF_INET, SOCK_STREAM)

        client_socket.connect((server_ip, server_port))

    except Exception as e:
        print(f"Server not found: {e}")


def receive_messages():
    while True:
        server_message = client_socket.recv(1024).decode()

        if server_message:
            print(f"\nReceived from server: {server_message}")
        else:
            print("Server closed the connection.")
            break


ip = input("Enter the server IP: ")
port = int(input("Enter the server port: "))

connect_to_server(ip, port)
print(f"Connected to {ip}")

Thread(target=receive_messages, daemon=True).start()

while True:
    message = input("> ").strip()
    if message:
        client_socket.sendall(message.encode())
        sleep(0.1)
