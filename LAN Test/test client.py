from socket import socket, AF_INET, SOCK_STREAM


def connect_to_server(ip, port):
    client_socket = socket(AF_INET, SOCK_STREAM)

    client_socket.connect((ip, port))

    client_socket.send("Hello from client".encode("utf-8"))

    response = client_socket.recv(1024).decode("utf-8")
    print(f"Server response {response}")

    client_socket.close()


server_ip = input("Enter the server IP: ")
server_port = int(input("Enter the server port: "))

connect_to_server(server_ip, server_port)
