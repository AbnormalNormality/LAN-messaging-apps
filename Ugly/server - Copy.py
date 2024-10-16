from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, gethostname, gethostbyname, SOL_SOCKET, SO_BROADCAST, error
from threading import Thread
from re import compile

from AliasGeneralFunctions import FormatConsole


def start_server(ip, port):
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)

    print(f"Started server at {ip}\nListening on port {port}...")
    open("chatLog.txt", "w").write(f"Started server at {ip}\nListening on port {port}...")

    while True:
        client_socket, client_address = server.accept()
        client_thread = Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


def handle_client(client_socket, client_address):
    print(f"{client_address[0]} connected")
    open("chatLog.txt", "a").write(f"\n{client_address[0]} connected")
    active_clients.append((client_socket, client_address))

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            server_message = f"{client_address[0]}: {FormatConsole.GREEN}{message}{FormatConsole.END}"
            server_message = compile(r"\x1b\[[0-9;]*[a-zA-Z]").sub("", server_message)

            open("chatLog.txt", "a").write(f"\n{server_message}")

            for tcs, _ in active_clients:
                tcs.sendall(server_message.encode())

        except error as e:
            if e.errno == 10054:
                pass

            else:
                print(e)
                break

        except Exception as e:
            print(e)
            break

    active_clients.remove((client_socket, client_address))
    client_socket.close()
    print(f"{client_address[0]} disconnected")
    open("chatLog.txt", "a").write(f"\n{client_address[0]} disconnected")


chat_log = []

active_clients = []

server_port = 1000

"""
server_port = input("Choose a server port (1-65535): ")
while not server_port.isdigit() or not 0 <= int(server_port) <= 65535:
    system("cls")
    server_port = input("Choose a server port (1-65535): ")
"""

start_server(gethostbyname(gethostname()), int(server_port))
