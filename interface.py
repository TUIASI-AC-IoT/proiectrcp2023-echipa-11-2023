import queue
import threading
import tkinter as tk
from functools import partial
from tkinter import ttk as subTK, simpledialog, messagebox

import commands as cmd
import events
import message_manager as msm


class Window(tk.Tk):
    def __init__(self, commandQ: queue.Queue, eventQ: queue.Queue):
        super().__init__()
        """To be updated in the future"""
        print('\ninterface, __init__')

        self.commmandQ = commandQ
        self.eventQ = eventQ

        self.event_listener = threading.Thread(target=self.EventListener, daemon=True)
        self.event_listener.start()

        # calea catre locatia curenta
        self.current_path = []
        self.current_path.append('')

        # prima comanda e list directory
        self.commmandQ.put(cmd.ListDirectory(self.current_path[0]))

        self.geometry("800x400")    # initial 800x200
        self.grid()

        # menu frame
        self.__menu = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        self.__menu.grid()
        self.__menu.pack(anchor="n", fill="x")

        # backward button
        """To do: add command"""
        self.__back = tk.Button(self.__menu, text="<<", command=None)
        self.__back.grid(column=0, row=0)

        # current path to directory
        self.__path = tk.Label(self.__menu, text=f"Downloads/{''.join(self.current_path)}")
        self.__path.grid(column=1, row=0)

        # refresh button
        self.__refresh = tk.Button(self.__menu, text="Refresh", command=self.Refresh)
        self.__refresh.grid(column=3, row=0)

        # ip display
        self.__ipVariable = tk.StringVar()
        self.__ip = tk.Entry(self.__menu, textvariable=self.__ipVariable)
        self.__ip.config(width=12)
        self.__ip.grid(column=4, row=0)

        # port display
        self.__portVariable = tk.IntVar()
        self.__port = tk.Entry(self.__menu)
        self.__port.configure(width=10)
        self.__port.grid(column=5, row=0)

        # button for connection type
        self.__commTypeVariable = tk.IntVar()
        self.__commType = tk.Checkbutton(self.__menu, text="Non-Confirmable", command=self.commandType, variable=self.__commTypeVariable)
        self.__commType.grid(column=6, row=0)

        # sub-menu for file list display
        self.__files = subTK.Treeview(self, columns=("type", "name"), show="headings", selectmode="browse")
        self.__files.heading("name", text="Name")
        self.__files["displaycolumns"] = ("name", )
        self.__scroll = subTK.Scrollbar(self.__files, orient="vertical", command=self.__files.yview)
        self.__files.configure(yscrollcommand=self.__scroll.set)
        self.__scroll.pack(side="right", fill="y")
        self.__files.pack(fill="x", side="bottom")

        #file actions
        self.__files.bind("<ButtonRelease-3>", self.fileActions)

        # menu frame
        self.__actions = tk.Frame(self, highlightcolor="black", highlightthickness=1)
        self.__actions.pack(fill="x", side="bottom")

        # create directory
        """To do: add command"""
        self.__createDir = tk.Button(self.__actions, text="Create directory", command=None)
        self.__createDir.grid(column=0, row=0)

        # file upload button
        """To do: add command"""
        self.__uploadButton = tk.Button(self.__actions, text="Upload file/directory", command=None)
        self.__uploadButton.grid(column=1, row=0)

    def fileActions(self, event):
        print('\n\nWindow, __filePopup')
        iid = self.__files.identify_row(event.y)
        name = self.__files.item(iid).get('values')[1]
        t = self.__files.item(iid).get('values')[0]
        if iid:
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Rename", command=partial(self.rename, name, iid, t))
            # menu.add_command(label="Delete", command=partial(self.__fileDelete, name, iid))
            # menu.add_command(label="Move", command=partial(self.__fileMove, name))
            # menu.add_command(label="Details", command=partial(self.__fileDetails, name))
            # if t == 0:
            #     menu.add_command(label="Download", command=partial(self.__fileDownload, name))
            menu.tk_popup(event.x_root, event.y_root, 1)

    def rename(self, name, row, tmp):
        newName = simpledialog.askstring(title=name, prompt="Enter new name:", initialvalue=name)
        print(name)
        temp = self.current_path.copy()
        temp.append(newName)

        if newName is not None:
            path = self.current_path.copy()
            # path.append(name)
            self.commmandQ.put(cmd.Rename(path, temp))
        else:
            messagebox.showerror("Error", "New name cannot be null")

    def commandType(self):
        cmd.CommunicationType = self.__commTypeVariable.get()

    def Refresh(self):
        """Refresh"""
        print('\ninterface, Refresh')
        self.commmandQ.put(cmd.ListDirectory(self.current_path))

    def EventListener(self):
        print('\ninterface, EventListener')
        while True:
            event: events.Event = self.eventQ.get()
            self.eventQ.task_done()

            if event.eventType == event.eventType.FILE_LIST:
                for item in self.__files.get_children():
                    self.__files.delete(item)   # stergem fisierele vechi

                files, path = event.data
                print('rrhoooooaaaaaaarrrrhhh', path)
                for item in files:
                    self.__files.insert('', tk.END, values=item)

                if type(path) == list():
                    if path[0] == '':
                        self.current_path = path
                    else:
                        self.current_path.clear()
                        self.current_path.append('')
                        for item in path:
                            self.current_path.append(item)    # refacem calea actuala
                elif path != '':
                    self.current_path.append(path)
                print(self.current_path)
                self.__path.configure(text='Dowloads/'.join(self.current_path))
