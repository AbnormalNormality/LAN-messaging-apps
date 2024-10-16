from tkinter import *
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, error
from threading import Thread

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, custom_rows, custom_columns, \
    clear_widgets, ScrollingFrame, Border

fix_resolution_issue()

main = Tk()
main.title("Client")

initiate_grid(main)
r, c = AliasTkFunctions.rows.get, AliasTkFunctions.columns.get

client_socket = socket(AF_INET, SOCK_STREAM)
broadcast_socket = socket(AF_INET, SOCK_DGRAM)

client_socket.setblocking(False)


class Screen:
    @staticmethod
    def connect():
        global server_list

        client_socket.close()

        resize_window(main, 4, 4)
        custom_rows(0, 1), custom_columns(1), clear_widgets()

        Button(text="Refresh", command=discover_servers).grid(row=0, column=0)

        server_list = Listbox(main)
        server_list.grid(row=1, column=0, sticky="nsew")
        server_list.bind("<Double-1>", connect_to_server)

        discover_servers()

    @staticmethod
    def home():
        global side_bar, chat_log

        resize_window(main, 2, 2)
        custom_rows(0, 0, 1, 0), custom_columns(1, 0, 3, 0), clear_widgets()

        Button(text="Disconnect", command=Screen.connect).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        top_bar = Label(text="Everyone", background="#e0e0e0")
        top_bar.grid(row=0, column=2, columnspan=2, sticky="nsew")

        Border(row=1, column=0, columnspan=c(), sticky="ew")

        side_bar = ScrollingFrame()
        side_bar.frame.grid(row=2, rowspan=r() - 1, column=0, sticky="nsew")

        Border(row=0, rowspan=r(), column=1, sticky="ns")

        message_box = Text(height=3, width=1, font="TkDefaultFont")
        message_box.grid(row=3, column=2, sticky="nsew")
        message_box.bind("<Return>", lambda event: send_message(message_box) if not event.state & 0x0001 else None)

        chat_log = ScrollingFrame()
        chat_log.frame.grid(row=2, column=2, columnspan=2, sticky="nsew")


def connect_to_server(event):
    global server_ip, server_port, client_socket

    if event:
        selection = server_list.curselection()
        if not selection:
            return

        index = selection[0]
        server_info = server_list.get(index)

        parts = server_info.split(", ")

        ip.set(parts[0].split(": ")[1])
        port.set(parts[1].split(": ")[1])

    try:
        server_ip, server_port = ip.get(), int(port.get())

        client_socket = socket(AF_INET, SOCK_STREAM)

        client_socket.connect((server_ip, server_port))

        Thread(target=lambda: listen_for_messages()).start()

        Screen.home()

    except Exception as e:
        print(f"Server not found: {e}")


def discover_servers():
    broadcast_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    broadcast_socket.sendto(b"DISCOVER", ("<broadcast>", 1000))

    main.after(100, listen_for_responses)


def listen_for_responses():
    global server_list

    server_list.delete("0", "end")

    broadcast_socket.settimeout(1)
    try:
        while True:
            response, addr = broadcast_socket.recvfrom(1024)
            server_info = response.decode()
            server_list.insert("end", server_info)

    except TimeoutError:
        pass


def listen_for_messages():
    while True:
        print("Looking for messages...")
        try:
            # Attempt to receive data with a timeout
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                print("Disconnected from server.")
                break

            print("Got message")
            print(f"Server: {message}")

            # Update the chat log with the new message
            main.after(0, lambda msg=message: Label(chat_log, msg).pack())

        except socket.timeout:
            # Timeout occurred, continue checking for messages
            continue

        except error as e:
            if e.errno == 10053:
                print("Connection was aborted.")
                break
            else:
                print(f"Error receiving message: {e}")
                break

        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def send_message(message_box):
    message = message_box.get("1.0", "end").strip()
    main.after_idle(lambda: message_box.delete("1.0", "end"))
    if not message:
        return

    client_socket.sendall(f"{message}".encode("utf-8"))


ip = StringVar(value="")
port = StringVar(value="1000")

server_ip = ""
server_port = 0

server_list = Listbox()

side_bar = ScrollingFrame()
chat_log = ScrollingFrame()

Screen.connect()

main.mainloop()
