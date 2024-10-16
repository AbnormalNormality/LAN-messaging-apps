# Important: EVERYTHING IS BROKEN AND I DON'T KNOW WHY
# ^^^ me fr fr
# That is you fucking idiot

from tkinter import *
from tkinter.ttk import Button
from random import choice
from socket import *
from tkinter.messagebox import showerror, askokcancel
from json import load, dump
from os.path import join, exists
from threading import Thread

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, custom_rows, custom_columns, \
    clear_widgets, Border, protect_grid_size, ScrollingFrame
from AliasNewPythonModule import folder_path

fix_resolution_issue()

main = Tk()
initiate_grid(main)
r, c = AliasTkFunctions.rows.get, AliasTkFunctions.columns.get
main.title(f"{choice(["YMCA!", "X < Y", "Why?", "y = mx + c"])}")
main.update_idletasks()
main.bind("<Configure>", lambda _: protect_grid_size())

ip = StringVar()
port = IntVar()
username = StringVar()

user_file = join(folder_path, "Yuser.json")
if exists(user_file) and open(user_file).read():
    user = load(open(user_file))
    ip.set(user.get("ip", ""))
    port.set(user.get("port", ""))
    username.set(user.get("username", ""))

client_log: ScrollingFrame | None = None
client_input: Text | None = None

server_log: ScrollingFrame | None = None
server_input: Text | None = None


class Show:
    @staticmethod
    def choose():
        main.protocol("WM_DELETE_WINDOW", main.destroy)

        clear_widgets()
        resize_window(main, 4, 4)
        custom_rows(1, 1, 1, 1, 1), custom_columns(1, 1)

        main.after_idle(lambda x=2: [main.columnconfigure(i, minsize=main.winfo_width() // x) for i in range(x)])

        Label(text="Y", font=("Lucida Fax", 14)).grid(row=0, column=0, columnspan=c())

        label_kwargs = dict(column=0, sticky="e", padx=(0, 10))
        entry_kwargs = dict(column=1, sticky="w", padx=(10, 0))

        Label(text="Username:").grid(row=1, **label_kwargs)
        Entry(textvariable=username, width=13, validate="key",
              validatecommand=(main.register(lambda chars: not (len(chars) > 8 or (not chars.isalnum() and chars != "_")
                                                                and chars != "")), "%P")).grid(row=1, **entry_kwargs)

        def is_valid_ip(ip_address):
            if len(ip_address) > 15:
                return False

            if ip_address == "":
                return True

            if ".." in ip_address:
                return False

            octets = ip_address.split('.')

            if len(octets) > 4:
                return False

            for octet in octets:
                if octet == "":
                    continue
                if not octet.isdigit():
                    return False
                if len(octet) > 3 or not (0 <= int(octet) <= 255):
                    return False
                if octet == "00":
                    return False

            return True

        Label(text="IP:").grid(row=2, **label_kwargs)
        Entry(textvariable=ip, width=13, validate="key",
              validatecommand=(main.register(is_valid_ip), "%P")).grid(row=2, **entry_kwargs)

        Label(text="Port:").grid(row=3, **label_kwargs)
        Spinbox(textvariable=port, width=5, from_=1024, to=1028, state="readonly").grid(row=3, **entry_kwargs)

        Button(text="Host", command=Show.server_and_client).grid(row=r() - 1, column=0, columnspan=(c() + 1) // 2)
        Button(text="Join", command=Show.client_only).grid(row=r() - 1, column=c() // 2, columnspan=(c() + 1) // 2)

        Border(dict(background="#a0a0a0"), row=0, column=c() // 2 - 1, columnspan=r(), sticky="sew", padx=20)
        Border(dict(background="#a0a0a0"), row=r() - 1, column=c() // 2 - 1, columnspan=r(), sticky="new", padx=20)
        Border(dict(background="#a0a0a0"), row=r() - 1, column=c() // 2 - 1, sticky="nse", pady=15)

    @staticmethod
    def client_only():
        global client_log, client_input

        client.connect_to_server(ip.get() if ip.get() else client.ip, port.get())

        if not client.connected:
            return

        clear_widgets()
        resize_window(main, 2, 2)
        custom_rows(1, 0), custom_columns(1)

        Label(text="Client", pady=10, font="TkDefaultFont 11").grid(row=0, column=1, sticky="nsew")
        client_log = ScrollingFrame()
        client_log.frame.grid(row=1, column=1, sticky="nsew")
        client_input = Text(height=2, font="TkDefaultFont 9")
        client_input.grid(row=r() - 1, column=1, sticky="nsew")

        client_input.bind("<Return>", lambda event: (client.send_message(client_input.get("0.0", "end")),
                          main.after_idle(lambda: client_input.delete("0.0", "end")))
                          if not event.state & 0x0001 else None)
        client_input.bind("<KeyPress>", lambda event: limit_text_input(event, client_input))

    @staticmethod
    def server_and_client():
        global server_log, server_input, client_log, client_input

        server.start_server(port.get())

        client.connect_to_server(ip.get() if ip.get() else client.ip, port.get())

        if not client.connected:
            return

        clear_widgets()
        resize_window(main, 2, 2)
        custom_rows(0, 1, 0), custom_columns(1, 1)

        Label(text="Server", pady=10, font="TkDefaultFont 11").grid(row=0, column=0, sticky="nsew")
        server_log = ScrollingFrame()
        server_log.frame.grid(row=1, column=0, sticky="nsew")
        server_input = Text(height=2, font="TkDefaultFont 9")
        server_input.grid(row=r() - 1, column=0, sticky="nsew")

        server_input.bind("<Return>", lambda event: (server.send_message(server_input.get("0.0", "end")),
                          main.after_idle(lambda: server_input.delete("0.0", "end")))
                          if not event.state & 0x0001 else None)
        server_input.bind("<KeyPress>", lambda event: limit_text_input(event, server_input))

        Label(text="Client", pady=10, font="TkDefaultFont 11").grid(row=0, column=1, sticky="nsew")
        client_log = ScrollingFrame()
        client_log.frame.grid(row=1, column=1, sticky="nsew")
        client_input = Text(height=2, font="TkDefaultFont 9")
        client_input.grid(row=r() - 1, column=1, sticky="nsew")

        client_input.bind("<Return>", lambda event: (client.send_message(client_input.get("0.0", "end")),
                          main.after_idle(lambda: client_input.delete("0.0", "end")))
                          if not event.state & 0x0001 else None)
        client_input.bind("<KeyPress>", lambda event: limit_text_input(event, client_input))

        Border(row=0, rowspan=r(), column=0, sticky="nse")
        Border(row=0, column=0, sticky="sew")
        Border(row=0, column=1, sticky="sew")


class Client(socket):
    def __init__(self):
        self.server = ("0.0.0.0", 0)
        self.username = ""
        self.connected = False
        self.ip = gethostbyname(gethostname())
        self.serverOwner = False

        super().__init__(AF_INET, SOCK_STREAM)
        self.settimeout(0.1)

    def connect_to_server(self, server_ip: str, server_port: int):
        self.server = (server_ip, server_port)
        self.username = username.get() if username.get() else "New User"
        self.serverOwner = self.ip == server_ip

        super().__init__(AF_INET, SOCK_STREAM)

        try:
            self.connect(self.server)
            self.connected = True
            dump({"ip": self.server[0], "port": self.server[1], "username": self.username}, open(user_file, "w"))
            Thread(target=self.receive_messages, daemon=True).start()
        except timeout:
            showerror("Error", f"Could not find server {self.server[0]} on port {self.server[1]}")
            self.connected = False
            return
        except ConnectionRefusedError:
            showerror("Error", f"{self.server[0]} is not hosting a server on port {self.server[1]}")
            self.connected = False
            return

        if not self.serverOwner:
            main.protocol("WM_DELETE_WINDOW", lambda: (self.close(), Show.choose()))

    def send_message(self, message: str):
        try:
            self.sendall(message.encode("utf-8"))
        except ConnectionAbortedError:
            client_input.configure(state="disabled")
            client_input.unbind_all("<Return>")

    def receive_messages(self):
        while True:
            try:
                message = self.recv(1024).decode("utf-8")

                if not message:
                    print("Client-side: Server closed the connection.")
                    break

                self.log(message)

            except timeout:
                pass

            except (ConnectionAbortedError, ConnectionResetError):
                try:
                    client_input.configure(state="disabled")
                    client_input.unbind_all("<Return>")
                    break
                except TclError:
                    break

    def log(self, message, **kwargs):
        Label(client_log, text=message, **kwargs).pack()


class Server(socket):
    def __init__(self):
        self.port = 0
        self.activeClients = []
        self.open = False

        super().__init__(AF_INET, SOCK_STREAM)

    def start_server(self, server_port: int):
        self.port = server_port
        self.activeClients.clear()

        super().__init__(AF_INET, SOCK_STREAM)
        self.bind(("0.0.0.0", self.port))
        self.listen(16)  # Client limit
        self.open = True

        main.protocol("WM_DELETE_WINDOW", lambda: (client.close(), self.close_server(), Show.choose()) if askokcancel(
            "Warning", "Are you sure you want to close the server?") else None)

        def accept_clients():
            while self.open:
                try:
                    client_socket, client_address = self.accept()
                    Thread(target=self.handle_client, args=(client_socket, client_address)).start()
                except OSError:
                    pass

        Thread(target=accept_clients).start()

    def close_server(self):
        self.close()
        self.open = False

    def send_message(self, message: str):
        for tcl, _ in self.activeClients:
            tcl.sendall(message.encode("utf-8"))

    def handle_client(self, client_socket, client_address):
        self.activeClients.append((client_socket, client_address))

        while True:
            try:
                message = self.recv(1024).decode("utf-8")

                if not message:
                    break

            except timeout:
                pass

            except error as e:
                if e.errno == 10054:
                    break
                elif e.errno == 10057:
                    break

                else:
                    # For debugging
                    print(f"Server-side: (error) {e}")
                    break

            except Exception as e:
                # For debugging
                print(f"Server-side: {e}")
                break

        self.activeClients.remove((client_socket, client_address))
        client_socket.close()


def limit_text_input(event, text: Text):
    if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Up", "Down"):
        return

    elif len(text.get("1.0", "end-1c")) >= 150:
        return "break"


client = Client()
server = Server()

Show.choose()

main.mainloop()
