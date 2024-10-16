from tkinter import *
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, custom_rows, custom_columns, \
    ScrollingFrame, Border, clear_widgets

fix_resolution_issue()

main = Tk()
resize_window(main, 2, 2)
main.title("Harmony - Client")

initiate_grid(main)
r, c = AliasTkFunctions.rows.get, AliasTkFunctions.columns.get

client_socket = socket(AF_INET, SOCK_STREAM)
broadcast_socket = socket(AF_INET, SOCK_DGRAM)


def update_server_list():
    clear_widgets(side_bar)

    broadcast_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    broadcast_socket.sendto(b"DISCOVER", ("<broadcast>", 1000))

    servers = listen_for_responses()

    for server in servers:
        label = Label(side_bar, text=f"{server[0]}:{server[1]}")
        label.pack(fill="x")
        label.bind("<Button-1>", lambda _: update_chat(*server))


def listen_for_responses():
    server_list = []

    broadcast_socket.settimeout(1)

    try:
        while True:
            response, addr = broadcast_socket.recvfrom(1024)
            server_info = response.decode()

            server_list.append(server_info.split(":"))

    except TimeoutError:
        pass

    return server_list


def update_chat(ip, port):
    print(ip, port)


custom_rows(0, 0, 1, 0), custom_columns(1, 0, 2), clear_widgets()

Button(text="Refresh server list", command=update_server_list).grid(row=0, column=0, sticky="nsew")

Label(background="#e0e0e0").grid(row=0, column=2, sticky="nsew")

Border(row=1, column=1, columnspan=c() - 1, sticky="ew")

side_bar = ScrollingFrame(background="#ffffff")
side_bar.frame.grid(row=1, rowspan=r() - 1, column=0, sticky="nsew")

Border(row=0, rowspan=r(), column=1, sticky="ns")

log_frame = ScrollingFrame(background="#ffffff")
log_frame.frame.grid(row=1, rowspan=r() - 1, column=2, sticky="nsew")

text_box = Text(height=3, width=1, font="TkDefaultFont 10")
text_box.grid(row=r() - 1, column=c() - 1, sticky="nsew")

main.mainloop()
