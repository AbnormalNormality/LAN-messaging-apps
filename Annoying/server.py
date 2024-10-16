from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname, error
from threading import Thread


class Server(socket):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.active_clients = []

        super().__init__(AF_INET, SOCK_STREAM)
        self.bind(("0.0.0.0", self.port))
        self.listen(5)

        print(f"Started server at {self.ip}\nListening on port {self.port}...")

        while True:
            client_socket, client_address = self.accept()
            Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def  handle_client(self, client_socket, client_address):
        self.active_clients.append((client_socket, client_address))

        print(f"{client_address[0]} connected")

        for tcs, _ in self.active_clients:
            tcs.sendall(f"@server:server:{client_address[0]} connected".encode("utf-8"))

        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if not message:
                    break

                # message = f"{client_address[0]}:{message}"
                # parts = message.split(":")
                # print(f"{parts[0]}: {parts[1]}")
                print(message)

                for tcs, _ in self.active_clients:
                    tcs.sendall(message.encode("utf-8"))

            except error as e:
                if e.errno == 10054:
                    break

                else:
                    print(e)
                    break

            except Exception as e:
                print(e)
                break

        self.active_clients.remove((client_socket, client_address))
        client_socket.close()

        print(f"{client_address[0]} disconnected")

        for tcs, _ in self.active_clients:
            tcs.sendall(f"@server:server:{client_address[0]} disconnected".encode("utf-8"))


server_port = 1000

Server(gethostbyname(gethostname()), server_port)
