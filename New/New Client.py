from tkinter import *
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname, timeout
from tkinter.messagebox import showerror
from os.path import exists
from json import load, dump, JSONDecodeError
from datetime import datetime
from threading import Thread

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, custom_rows, custom_columns, \
    clear_widgets, Border, ScrollingFrame, ToolTip

from sharedFunctions import Validate

fix_resolution_issue()

main = Tk()
resize_window(main, 4, 4)
main.title("New Client")
main.attributes("-topmost", True)

client_data = {}
if exists("client.json") and open("client.json").read():
    client_data |= load(open("client.json"))
main.protocol("WM_DELETE_WINDOW", lambda: (dump(client_data, open("client.json", "w")), main.destroy()))

initiate_grid(main)
r, c = AliasTkFunctions.rows.get, AliasTkFunctions.columns.get

port = Entry()
ip = Entry()
username = Entry()
client_log = ScrollingFrame()
entry = Text()


class Show:
    @staticmethod
    def connecting():
        global port, ip, username

        clear_widgets()
        resize_window(main, 4, 4, x="current", y="current")
        custom_rows(1, 1, 1, 1), custom_columns(1, 1)

        Border({"background": "#a0a0a0"}).grid(row=0, column=0, columnspan=c(), sticky="new")

        Label(text="Username:").grid(row=0, column=0, sticky="e", padx=(0, 10))
        username = Entry(width=13, validate="key", validatecommand=(main.register(Validate.username), "%P"))
        username.grid(row=0, column=1, sticky="w")
        username.insert("0", client_data.get("username", ""))

        Border({"background": "#a0a0a0"}).grid(row=0, column=0, columnspan=c(), sticky="sew")

        Label(text="Ip:").grid(row=1, column=0, sticky="e", padx=(0, 10))
        ip = Entry(width=13, validate="key", validatecommand=(main.register(Validate.ip), "%P"))
        ip.grid(row=1, column=1, sticky="w")
        ip.insert("0", client_data.get("server_ip", ""))

        Label(text="Port:").grid(row=2, column=0, sticky="e", padx=(0, 10))
        port = Entry(width=5, validate="key", validatecommand=(main.register(Validate.port), "%P"))
        port.grid(row=2, column=1, sticky="w")
        port.insert("0", client_data.get("server_port", ""))

        Border({"background": "#a0a0a0"}).grid(row=2, column=0, columnspan=c(), sticky="sew")

        Button(text="Connect", command=client.connect_to_server).grid(row=r() - 1, column=0, columnspan=c())

    @staticmethod
    def messaging():
        global client_log, entry

        clear_widgets()
        resize_window(main, 2, 2, x="current", y="current")
        custom_rows(1, 0), custom_columns(2, 1)

        client_log = ScrollingFrame(background="#ffffff", pady=5, padx=5)
        client_log.frame.grid(row=0, column=0, sticky="nsew")

        entry = Text(width=1, height=3, font="TkDefaultFont 9")
        entry.grid(row=1, column=0, sticky="nsew")
        entry.bind("<Return>", lambda event: (client.send_message(entry.get("0.0", "end")),
                                              main.after_idle(lambda: entry.delete("0.0", "end")))
                   if not event.state & 0x0001 else None)

        Border().grid(row=0, rowspan=r(), column=0, sticky="nse")

        Border({"background": "#a0a0a0"}).grid(row=0, column=0, columnspan=c(), sticky="new")


class Client(socket):
    def __init__(self):
        self.server_ip = ""
        self.server_port = 0
        self.username = ""
        self.ip = gethostbyname(gethostname())

        super().__init__(AF_INET, SOCK_STREAM)
        self.settimeout(0.25)

    def connect_to_server(self):
        self.server_ip = ip.get() if ip.get() else self.ip
        self.username = username.get() if username.get() else self.ip

        try:
            self.server_port = int(port.get())
            self.connect((self.server_ip, self.server_port))
            self.send(self.username.encode("utf-8"))  # Send username
        except ValueError:
            showerror(main.title(), f"Invalid server port")
            return
        except OverflowError:
            showerror(main.title(), f"Invalid server port {self.server_port} (port > 65535)")
            return
        except OSError:
            showerror(main.title(), f"The server {self.server_ip} does not exist")
            return

        client_data.update({"server_ip": self.server_ip, "server_port": self.server_port, "username": self.username})

        Thread(target=self.receive_messages, daemon=True).start()

        Show.messaging()

    def receive_messages(self):
        while True:
            try:
                raw_message = self.recv(1024).decode("utf-8")
                sender_ip, sender_username, message = raw_message.split(" ", 2)

                if not raw_message:
                    raise ConnectionResetError

                log(message, sender_ip=sender_ip, sender_username=sender_username)

            except timeout:
                pass

            except ConnectionResetError:
                entry.configure(state="disabled")
                showerror(main.title(), "Server closed")  # TODO: Change once log is added
                break

    def send_message(self, message):
        formatted_message = message

        formatted_message = "\n".join([line.strip() for line in formatted_message.split("\n") if line.strip()])

        self.sendall(formatted_message.encode("utf-8"))


def log(message, tooltip="", sender_ip="", sender_username=None, **specific_kwargs):
    global last_sender

    if message.startswith("("):
        try:
            end_dict_index = message.find(")") + 1

            param_part = message[:end_dict_index]

            param_part = param_part[1:-1].strip()
            kwargs_pairs = param_part.split(",")

            custom_kwargs = {}
            for pair in kwargs_pairs:
                key, value = pair.split("=", 1)
                custom_kwargs[key.strip()] = value.strip().strip("\"")

                message = message[end_dict_index:].lstrip()

                Label(**custom_kwargs).destroy()

        except (ValueError, IndexError, JSONDecodeError, ValueError, TclError):
            custom_kwargs = {}
    else:
        custom_kwargs = {}

    if sender_ip == "":
        kwargs = (dict(), dict())
    else:
        kwargs = (dict(justify="left" if sender_ip != client.ip else "right"),
                  dict(anchor="w" if sender_ip != client.ip else "e"))

    if sender_ip != "" and last_sender != sender_ip:
        last_sender = sender_ip
        if sender_username and sender_username not in ["@server"]:
            log(f"{sender_username}", sender_ip=sender_ip, sender_username="@server",
                font="TkDefaultFont 9 underline")

    scroll_to_bottom = client_log.canvas.yview()[1] == 1.0

    label = Label(client_log, text=message, wraplength=client_log.winfo_width() - 10,
                  background=client_log.cget("background"), **specific_kwargs | custom_kwargs | kwargs[0])
    label.pack(**kwargs[1])

    tooltip = f"{tooltip}\n{datetime.now().strftime("%I:%M:%S %p\n%d/%m/%Y")}".strip()

    ToolTip(label, text=tooltip, wraplength=350, wait_time=150, x_offset=30, y_offset=5, follow=True)

    if scroll_to_bottom:
        main.after_idle(lambda: client_log.canvas.yview_moveto(1.0))


client = Client()

main.update()
Show.connecting()

last_sender = ""

main.mainloop()
