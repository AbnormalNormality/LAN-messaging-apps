from tkinter import *
from socket import socket, AF_INET, SOCK_STREAM, timeout, gethostname, gethostbyname
from threading import Thread
from json import dump, load, JSONDecodeError
from os.path import exists
from tkinter.messagebox import showerror
from plyer import notification
from tkinter.font import Font

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, custom_rows, custom_columns, \
    clear_widgets, ScrollingFrame, Border, ToolTip

fix_resolution_issue()

main = Tk()
main.title("Client")
# main.attributes("-topmost", True)

initiate_grid(main)
r, c = AliasTkFunctions.rows.get, AliasTkFunctions.columns.get


class Show:
    @staticmethod
    def connecting():
        clear_widgets()
        resize_window(main, 5, 5)
        custom_rows(1, 1, 1, 1), custom_columns(1, 1)

        def validate_username(chars):
            if len(chars) > 8 or (not chars.isalnum() and chars != "_") and chars != "":
                return False

            return True

        Label(text="Username:").grid(row=0, column=0, sticky="e", padx=(0, 10))
        Entry(width=13, textvariable=username_var, validate="key",
              validatecommand=(main.register(validate_username), "%P")).grid(row=0, column=1, sticky="w")

        def validate_ip(chars):
            if len(chars) > 15:
                return False

            return True

        Label(text="Ip:").grid(row=1, column=0, sticky="e", padx=(0, 10))
        Entry(width=13, textvariable=ip_var, validate="key", validatecommand=(main.register(validate_ip), "%P")).grid(
            row=1, column=1, sticky="w")

        def validate_port(chars):
            if (not chars.isdigit() and chars != "") or len(chars) > 5:
                return False

            return True

        Label(text="Port:").grid(row=2, column=0, sticky="e", padx=(0, 10))
        Entry(width=5, textvariable=port_var, validate="key",
              validatecommand=(main.register(validate_port), "%P")).grid(row=2, column=1, sticky="w")

        Button(text="Connect", command=Show.messaging).grid(row=r() - 1, column=0, columnspan=c())

    @staticmethod
    def messaging():
        global frame, text

        clear_widgets()
        resize_window(main, 3, 3)
        custom_rows(0, 0, 1, 0), custom_columns(1)

        Label(background="#e0e0e0").grid(row=0, column=0, sticky="nsew")

        Border().grid(row=1, column=0, sticky="ew")

        frame = ScrollingFrame(padx=5)
        frame.frame.grid(row=2, column=0, sticky="nsew")
        frame.update()

        def limit_text_input(event):
            if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Up", "Down"):
                return

            elif len(text.get("1.0", "end-1c")) >= 150:
                return "break"

        text = Text(width=1, height=3, font="TkDefaultFont 10")
        text.grid(row=3, column=0, sticky="nsew")
        text.bind("<Return>", lambda event: (client.send_message(text.get("0.0", "end")),
                                             main.after_idle(lambda: text.delete("0.0", "end")))
                  if not event.state & 0x0001 else None)
        text.bind("<KeyPress>", limit_text_input)

        try:
            client = Client(ip_var.get(), int(port_var.get()), username_var.get(), frame, text)

        except Exception as e:
            print(e)
            Show.connecting()
            return


class Client(socket):
    def __init__(self, ip, port, username, log_frame, input_widget):
        self.ip = ip
        self.port = port
        self.log_frame = log_frame
        self.user = gethostbyname(gethostname())
        self.username = username if username else gethostbyname(gethostname())
        self.last_sender = "0.0.0.0"
        self.input_widget = input_widget

        super().__init__(AF_INET, SOCK_STREAM)

        self.settimeout(5)
        try:
            self.connect((self.ip, self.port))
            dump((self.username, self.ip, self.port), open("user.json", "w"))

            Thread(target=self.receive_messages, daemon=True).start()

        except timeout:
            showerror(main.title(), "Server not reachable (timed out)")
            Show.connecting()

        except Exception as e:
            showerror(main.title(), f"Connection error: {e}")
            Show.connecting()

    def send_message(self, message):
        if not message.strip():
            return

        message = self.user + ":" + self.username + ":" + "\n".join([line.strip() for line in message.split("\n") if
                                                                     line.strip()])

        self.sendall(message.encode("utf-8"))

    def receive_messages(self):
        while True:
            try:
                message = self.recv(1024).decode("utf-8")
                parts = message.split(":", 2)

                if message:
                    if parts[0] == "@server":
                        kwargs = (dict(), dict())
                    else:
                        kwargs = (dict(justify="left" if parts[0] != self.user else "right"),
                                  dict(anchor="w" if parts[0] != self.user else "e"))

                    if parts[2].startswith("("):
                        try:
                            end_dict_index = parts[2].find(")") + 1

                            param_part = parts[2][:end_dict_index]

                            param_part = param_part[1:-1].strip()
                            kwargs_pairs = param_part.split(",")

                            custom_kwargs = {}
                            for pair in kwargs_pairs:
                                key, value = pair.split("=", 1)
                                custom_kwargs[key.strip()] = value.strip().strip("\"")

                            parts[2] = parts[2][end_dict_index:].lstrip()

                            Label(**custom_kwargs).destroy()

                        except (ValueError, IndexError, JSONDecodeError, ValueError, TclError):
                            custom_kwargs = {}

                    # dict() ^^^
                    # TODO: Allow use of kwargs that use (), e.g. font=("System", 14)

                    elif parts[2].startswith("{"):
                        try:
                            end_dict_index = parts[2].find("}") + 1

                            custom_kwargs = eval(parts[2][:end_dict_index])

                            parts[2] = parts[2][end_dict_index:].lstrip()

                            Label(**custom_kwargs).destroy()

                        except (ValueError, IndexError, JSONDecodeError, ValueError, TclError, NameError):
                            custom_kwargs = {}

                    else:
                        custom_kwargs = {}

                    # {} ^^^
                    # TODO: Patch, currently uses eval, maybe keep?

                    # Testing $(Hell)
                    raw_message = parts[2]

                    command_pairs = []
                    current_pair = None

                    for index, char in enumerate(raw_message):
                        if char in "!?$" and index != len(raw_message) - 1 and raw_message[index + 1] == "[":
                            current_pair = [index]

                        elif isinstance(current_pair, list) and char == "[":
                            current_pair.append(index)

                        elif isinstance(current_pair, list) and char == "]":
                            current_pair.append(raw_message[current_pair[1] + 1:index])
                            current_pair.append(index)
                            command_pairs.append(current_pair)
                            current_pair = None

                        # print(index, char)

                    filtered_message = raw_message

                    if True:
                        for pair in command_pairs:
                            print(f"{pair}: {[raw_message[i] if isinstance(i, int) else i for i in pair]}")

                    for pair in list(reversed(command_pairs)):
                        str_pair = [raw_message[i] if isinstance(i, int) else i for i in pair]
                        combined = "".join(str_pair)
                        replacement = ""
                        contents = str_pair[2]

                        font = custom_kwargs.get("font", ["TkDefaultFont", 9])
                        if type(font) is str:
                            font = font.split(" ")

                        if combined.startswith("$"):

                            if contents.startswith("#") and len(contents) in [4, 7] and all(ch in "0123456789abcdef" for
                                                                                            ch in contents[1:]):
                                custom_kwargs.update({"fg": contents})

                            elif contents.isdigit() and int(contents) > 0:
                                font[1] = int(contents)

                            else:
                                font[0] = contents

                            custom_kwargs.update({"font": font})

                        elif combined.startswith("?"):
                            try:
                                replacement = eval(contents)
                            except (NameError, SyntaxError):
                                pass

                        filtered_message = f"{filtered_message[:pair[0]]}{replacement}{filtered_message[pair[-1] + 1:]}"

                    parts[2] = filtered_message

                    #

                    if not parts[2].strip():
                        continue

                    if self.last_sender != parts[0]:
                        self.last_sender = parts[0]
                        if parts[0] != "@server":
                            Label(self.log_frame, text=parts[1], font="TkDefaultFont 9 underline",
                                  wraplength=self.log_frame.winfo_width(), **kwargs[0]).pack(**kwargs[1])

                    label = Label(self.log_frame, text=parts[2], wraplength=self.log_frame.winfo_width(),
                                  **kwargs[0], **custom_kwargs)
                    label.pack(**kwargs[1])

                    def quote(quoted_message):
                        self.input_widget.delete("1.0", "end")
                        self.input_widget.insert("1.0", f"(font=TkDefaultFont 9 italic)\"{quoted_message.strip()}\"\n")
                    
                    label.bind("<Button-1>", lambda _, quoted_message=parts[2]: quote(quoted_message))
                    ToolTip(label, text=message, wraplength=350, x_change=50, y_change=10)

                    main.after_idle(lambda: self.log_frame.canvas.yview_moveto("1.0"))

                    if f"@{self.username}" in parts[2] or "@everyone" in parts[2]:
                        notification.notify(title="New Message", message=parts[2], app_name="Client", timeout=5)

                else:
                    print("Server closed the connection.")
                    break

            except timeout:
                pass

            except ConnectionResetError:
                Label(self.log_frame, text="Server closed").pack()
                self.input_widget.configure(state="disabled")
                self.input_widget.unbind_all("<Return>")
                break


username_var = StringVar(value="User")
ip_var = StringVar(value="0.0.0.0")
port_var = StringVar(value="0")

if exists("user.json"):
    user = load(open("user.json"))
    if len(user) == 3:
        username_var.set(user[0])
        ip_var.set(user[1])
        port_var.set(user[2])

frame = ScrollingFrame()
text = Text()

Show.connecting()

main.mainloop()
