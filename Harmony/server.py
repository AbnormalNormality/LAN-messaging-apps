from tkinter import *
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, custom_rows, custom_columns, \
    ScrollingFrame, Border, clear_widgets

fix_resolution_issue()

main = Tk()
resize_window(main, 3, 3)
main.title("Harmony - Server")

initiate_grid(main)
r, c = AliasTkFunctions.rows.get, AliasTkFunctions.columns.get


class Server:
    @staticmethod
    def start(ip, port):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(("0.0.0.0", port))
        server.listen(5)

        LogMessage(f"Started server at {ip}")
        LogMessage(f"Listening on port {port}...")

        def scan():
            Server.handle_client(*server.accept())
            main.after(100, lambda *_: scan())

        Thread(target=scan).start()

        Thread(target=Server.listen_for_broadcasts, args=(ip, port)).start()

    @staticmethod
    def stop():
        start_button.configure(text="Start server", command=Server.handle_start)

    @staticmethod
    def handle_start():
        start_button.configure(text="Stop server", command=Server.stop)
        clear_widgets(log_frame)

        Server.start(gethostbyname(gethostname()), 1000)

    @staticmethod
    def handle_client(client_socket, client_address):
        print(f"{client_address[0]} connected")

    @staticmethod
    def listen_for_broadcasts(ip, port):
        broadcast_socket = socket(AF_INET, SOCK_DGRAM)
        broadcast_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        broadcast_socket.bind(("", port))

        while True:
            data, addr = broadcast_socket.recvfrom(1024)
            if data.decode() == "DISCOVER":
                response = f"{ip}:{port}"

                broadcast_socket.sendto(response.encode(), addr)


class LogMessage(Label):
    def __init__(self, message):
        super().__init__(log_frame, text=message, wraplength=log_frame.winfo_width(), justify="left",
                         background=log_frame.cget("background"))
        self.pack(anchor="w", padx=10, pady=(5, 0), fill="x")
        main.after_idle(lambda: log_frame.canvas.yview_moveto(1.0))


custom_rows(1), custom_columns(1, 0, 1)

log_frame = ScrollingFrame(background="#ffffff")
log_frame.frame.grid(row=0, rowspan=r(), column=0, sticky="nsew")

Border(row=0, rowspan=r(), column=1, sticky="ns")

start_button = Button(text="Start server", command=Server.handle_start)
start_button.grid(row=0, column=2)

main.mainloop()
