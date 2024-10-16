from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname


def start_server(ip, port):
    server = socket(AF_INET, SOCK_STREAM)

    server.bind(("0.0.0.0", port))

    server.listen(5)
    print(f"Started server at {ip}\nListening on port {port}...")

    while True:
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address}")

        data = client_socket.recv(1024).decode("utf-8")
        print(f"Received {data}")

        client_socket.send("Hello from server".encode("utf-8"))

        client_socket.close()


server_ip = gethostbyname(gethostname())
server_port = 12345

start_server(server_ip, server_port)
