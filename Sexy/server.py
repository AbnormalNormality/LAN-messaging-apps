from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, gethostname, gethostbyname, SOL_SOCKET, SO_BROADCAST
from threading import Thread

from AliasGeneralFunctions import FormatConsole


def start_server(ip, port):
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"Started server at {ip}\nListening on port {port}...")

    Thread(target=listen_for_broadcasts, args=(ip, port)).start()

    while True:
        client_socket, client_address = server.accept()
        client_thread = Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


def listen_for_broadcasts(ip, port):
    broadcast_socket = socket(AF_INET, SOCK_DGRAM)
    broadcast_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    broadcast_socket.bind(("", port))

    while True:
        try:
            data, addr = broadcast_socket.recvfrom(1024)
            if data.decode() == "DISCOVER":
                response = f"Server IP: {ip}, Port: {port}"
                broadcast_socket.sendto(response.encode(), addr)
                print(f"Responded to {addr}: {response}")
        except Exception as e:
            print(f"Error listening for broadcasts: {e}")


def handle_client(client_socket, client_address):
    print(f"{client_address}: Connected")
    active_clients.append((client_socket, client_address))

    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                print(f"{client_address}: Disconnected")
                break

            print(f"{client_address}: {FormatConsole.GREEN}{message}{FormatConsole.END}")

            for tcs, _ in active_clients:
                try:
                    tcs.sendall(f"{client_address}: {message}")
                except Exception as e:
                    print(f"Error sending to {client_socket.getpeername()}: {e}")

        except Exception as e:
            print(f"{client_address}: Error handling client: {e}")
            break

    active_clients.remove((client_socket, client_address))
    client_socket.close()
    print(f"{client_address}: Closed connection")


active_clients = []

server_port = 1000

"""
server_port = input("Choose a server port (1-65535): ")
while not server_port.isdigit() or not 0 <= int(server_port) <= 65535:
    system("cls")
    server_port = input("Choose a server port (1-65535): ")
"""

start_server(gethostbyname(gethostname()), int(server_port))
