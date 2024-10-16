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


def listen_for_responses():
    server_list = []

    broadcast_socket.settimeout(1)

    try:
        while True:
            response, addr = broadcast_socket.recvfrom(1024)
            server_info = response.decode()

            parts = server_info.split(", ")

            server_list.append((parts[0].split(": ")[1], parts[1].split(": ")[1]))

    except TimeoutError:
        pass

    return server_list


def receive_messages():
    while True:
        server_message = client_socket.recv(1024).decode()

        if server_message:
            print(f"\nReceived from server: {server_message}")
        else:
            print("Server closed the connection.")
            break


broadcast_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
broadcast_socket.sendto(b"DISCOVER", ("<broadcast>", 1000))

servers = listen_for_responses()

if not servers:
    input("No servers found\nPress ENTER to exit")
    exit()

print("Servers found:")
    
for server in servers:
    print(f"{servers.index(server)}: {server[0]}")
        
print("\nType the number of the server you want to connect to:")
    
server = int(input(""))
    
connect_to_server(*servers[server])
print(f"Connected to {servers[server][0]}")

Thread(target=receive_messages, daemon=True).start()

while True:
    message = input("> ").strip()
    if message:
        client_socket.sendall(message.encode())
        sleep(0.1)
