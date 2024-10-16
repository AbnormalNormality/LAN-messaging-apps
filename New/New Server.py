from tkinter import *
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname, error
from datetime import datetime
from threading import Thread
from os.path import exists
from json import load, dump

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, custom_rows, custom_columns, \
    ScrollingFrame, Border, clear_widgets, ToolTip

from sharedFunctions import Validate

fix_resolution_issue()

main = Tk()
resize_window(main, 3, 3)
main.title("New Server")
main.attributes("-topmost", True)

server_data = {}
if exists("server.json") and open("server.json").read():
    server_data |= load(open("server.json"))
main.protocol("WM_DELETE_WINDOW", lambda: (dump(server_data, open("server.json", "w")), main.destroy()))

initiate_grid(main)
r, c = AliasTkFunctions.rows.get, AliasTkFunctions.columns.get

custom_rows(1, 1), custom_columns(3, 1, 1)

server_log = ScrollingFrame(background="#ffffff", border=True, pady=5)
server_log.frame.grid(row=0, rowspan=r(), column=0, sticky="nsew")

Border().grid(row=0, rowspan=r(), column=0, sticky="nse")

Border().grid(row=0, column=0, columnspan=c(), sticky="new")


def log(message: str, tooltip: str = "", **kwargs):
    scroll_to_bottom = server_log.canvas.yview()[1] == 1.0

    label = Label(server_log, text=message, wraplength=server_log.winfo_width() - 10,
                  background=server_log.cget("background"), **kwargs)
    label.pack()

    tooltip = f"{tooltip}\n{datetime.now().strftime("%I:%M:%S %p\n%d/%m/%Y")}".strip()

    ToolTip(label, text=tooltip, wraplength=350, wait_time=150, x_offset=30, y_offset=5, follow=True)

    if scroll_to_bottom:
        main.after_idle(lambda: server_log.canvas.yview_moveto(1.0))


class Server(socket):
    def __init__(self):
        self.ip = gethostbyname(gethostname())
        self.port = 0
        self.active_clients = []
        self.running = False

        super().__init__(AF_INET, SOCK_STREAM)

    def start(self):
        clear_widgets(server_log)

        super().__init__(AF_INET, SOCK_STREAM)

        try:
            self.port = int(port.get())
            self.bind(("0.0.0.0", self.port))
        except OverflowError:
            log(f"Invalid port {self.port} (port > 65535)", foreground="#cc0000")
            return
        except ValueError:
            log("Invalid port (port < 0)", foreground="#cc0000")
            return
        except OSError:
            log(f"Port {self.port} is unavailable", foreground="#cc0000")
            return

        server_data.update({"port": self.port})

        self.listen(5)
        self.running = True

        Thread(target=self.accept_clients, daemon=True).start()

        start_button.configure(text="Stop server", command=self.stop)
        port.configure(state="disabled")
        log(f"Started server at {gethostbyname(gethostname())}:{self.port}")

    def stop(self):
        self.running = False
        self.close()

        start_button.configure(text="Start server", command=self.start)
        port.configure(state="normal")
        log("Closed server")

    def accept_clients(self):
        while True:
            try:
                client_socket, client_address = self.accept()
                Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except OSError:
                if not self.running:
                    break
                else:
                    raise OSError

    def handle_client(self, client_socket, client_address):
        self.active_clients.append((client_socket, client_address))
        log(f"New client connect {client_address[0]}")
        username = client_socket.recv(1024).decode("utf-8")
        log(f"Client data initialised under {username}")

        for tsc, _ in self.active_clients:
            tsc.sendall(f" @server {username} connected".encode("utf-8"))

        while True:
            try:
                raw_message = client_socket.recv(1024).decode("utf-8")
                raw_message = f"{client_address[0]} {username} {raw_message}"
                sender_ip, sender_username, message = raw_message.split(" ", 2)

                if not raw_message:
                    break

                log(f"{client_address[0]}: {raw_message}")
                for tsc, _ in self.active_clients:
                    tsc.sendall(f"{sender_ip} {sender_username} {message}".encode("utf-8"))

            except error as e:
                if e.errno == 10054:
                    break

                else:
                    raise e

            except ConnectionAbortedError:
                break

        self.active_clients.remove((client_socket, client_address))
        client_socket.close()

        log(f"Client disconnected {client_address[0]}")


server = Server()

start_button = Button(text="Start server", command=server.start, width=9)
start_button.grid(row=r() - 1, column=1, columnspan=2)

Label(text="Port:").grid(row=0, column=1, sticky="e", padx=(0, 10))
port = Entry(width=5, validate="key", validatecommand=(main.register(Validate.port), "%P"))
port.grid(row=0, column=2, sticky="w")
port.insert("0", server_data.get("port", ""))

main.mainloop()
