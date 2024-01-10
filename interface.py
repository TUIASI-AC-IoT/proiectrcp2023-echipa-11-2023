import queue
import os.path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import functools
from tkinter import messagebox
from tkinter import filedialog
import events as ev
import communication_manager as comm
import commands as cmd
import events


class Window(tk.Tk):
    def __init__(self, commandQ: queue.Queue, eventQ: queue.Queue):
        super().__init__()
        """To be updated in the future"""
        print('\ninterface, __init__')

        self.commandQ = commandQ
        self.eventQ = eventQ

        self.event_listener = threading.Thread(target=self.EventListener, daemon=True)
        self.event_listener.start()

        # list of strings for the path
        self.current_path = []
        self.current_path.append('')

        self.geometry("800x400")    # initial 800x200
        self.grid()

        # menu frame
        self.__menu = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        self.__menu.grid()
        self.__menu.pack(anchor="n", fill="x")

        # backward button
        self.__back = tk.Button(self.__menu, text="<<", command=self.backward)
        self.__back.grid(column=0, row=0)

        # current path to directory
        self.__path = tk.Label(self.__menu, text=f"Downloads/{self.current_path[0]}")
        self.__path.grid(column=1, row=0)

        # refresh button
        self.__refresh = tk.Button(self.__menu, text="Refresh", command=self.Refresh)
        self.__refresh.grid(column=3, row=0)

        # ip display
        self.__ipVariable = tk.StringVar()
        self.__ip = tk.Entry(self.__menu, textvariable=self.__ipVariable)
        self.__ip.bind("<FocusOut>", self.setIp)
        self.__ip.config(width=12)
        self.__ip.grid(column=4, row=0)

        # port display
        self.__portVariable = tk.IntVar()
        self.__port = tk.Entry(self.__menu)
        self.__port.bind("<FocusOut>", self.setPort)
        self.__port.configure(width=10)
        self.__port.grid(column=5, row=0)

        # button for connection type
        self.__commTypeVariable = tk.IntVar()
        self.__commType = tk.Checkbutton(self.__menu, text="Non-Confirmable", command=self.setType, variable=self.__commTypeVariable)
        self.__commType.grid(column=6, row=0)

        # sub-menu for file list display
        self.__files = ttk.Treeview(self, columns=("type", "name"), show="headings", selectmode="browse")
        self.__files.heading("name", text="Name")
        self.__files["displaycolumns"] = ("name", )
        self.__scroll = ttk.Scrollbar(self.__files, orient="vertical", command=self.__files.yview)
        self.__files.configure(yscrollcommand=self.__scroll.set)
        self.__scroll.pack(side="right", fill="y")
        self.__files.pack(fill="both", expand=True)

        self.__files.bind("<ButtonRelease-3>", self.popup)
        self.__files.bind("<Double-1>", self.doubleClick)


        # menu frame
        self.__actions = tk.Frame(self, highlightcolor="black", highlightthickness=1)
        self.__actions.pack(fill="x", side="bottom")

        # create directory

        self.__createDir = tk.Button(self.__actions, text="Create directory", command=self.makeDirectory)
        self.__createDir.grid(column=0, row=0)

        # file upload button
        self.__uploadButton = tk.Button(self.__actions, text="Upload file/directory", command=self.uploadFile)
        self.__uploadButton.grid(column=1, row=0)

    def EventListener(self):
        while True:
            event: ev.Event = self.eventQ.get()

            if event.eventType == ev.EventType.FILE_LIST:
                for i in self.__files.get_children():
                    self.delete(i)

                (files, path) = event.data
                for i in files:
                    self.__files.insert("", tk.END, values=i)

                if path[0] == "":
                    self.current_path = path
                else:
                    self.current_path.clear()
                    self.current_path.append("")
                    for i in path:
                        self.current_path.append(i)
                temp = ""
                for i in path:
                    if i != "":
                        temp += "/" + i
                self.current_path.configure(text=temp)
            elif event.eventType == ev.EventType.FILE_HEADER:
                (path, content) = event.data
                messagebox.showinfo(path, content)
            elif event.eventType == ev.EventType.FILE_CONTENT:
                messagebox.showinfo("File downloaded succesfully!", event.data)
            elif event.eventType == ev.EventType.FAILED_REQUEST:
                messagebox.showerror("Request failed!", event.data)
            elif event.eventType == ev.EventType.REQUEST_TIMEOUT:
                messagebox.showerror("Request timeout", event.data)
            elif event.eventType == ev.EventType.DELETED_FILE:
                self.commandQ.put(cmd.ListDirectory(self.current_path))
            elif event.eventType == ev.EventType.RENAMED_FILE:
                self.commandQ.put(cmd.ListDirectory(self.current_path))
            elif event.eventType == ev.EventType.CREATED_FOLDER:
                if event.data[0:len(event.data) - 1] == self.current_path[1:len(self.current_path)]:
                    self.__files.insert("", tk.END, values=(0, event.data[-1]))
            elif event.eventType == ev.EventType.FILE_UPLOADED:
                if event.data[0:len(event.data) - 1] == self.__path[1:len(self.current_path)]:
                    self.__files.insert("", tk.END, values=(0, event.data[-1]))
            self.eventQ.task_done()

    def doubleClick(self, event):
        row = self.__files.identify_row(event.y)
        arr = self.__files.item(row).get('values')
        name = arr[1]
        temp = arr[2]
        if temp == 1:
            self.current_path.append(name)
            self.commandQ.put(cmd.ListDirectory(self.__path[1:len(self.current_path)]))


    def popup(self, event):
        row = self.__files.identify_row(event.y)
        arr = self.__files.item(row).get('values')
        name = arr[1]
        tmp = arr[0]

        if row:
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Details", command=functools.partial(self.details, name))
            menu.add_command(label="Rename", command=functools.partial(self.rename, name, row, tmp))
            menu.add_command(label="Move", command=functools.partial(self.move, name))
            menu.add_command(label="Delete", command=functools.partial(self.delete, name, row))

            if tmp == 0:
                menu.add_command(label="Download", command=functools.partial(self.download, name))

            menu.tk_popup(event.x_root, event.y_root, 1)

    def download(self, name):
        comm.DownloadDirectory = filedialog.askdirectory()
        path = self.current_path.copy()
        path.append(name)
        self.commandQ.put(cmd.Download(path))


    def delete(self, name):
        path = self.current_path.copy()
        path.append(name)
        self.commandQ.put(cmd.Delete(path))

    def move(self, name):
        newPath = simpledialog.askstring(title="Path", prompt="Enter the path to move the file into (using \'\\\'): ")
        if newPath is not None:
            path = self.current_path.copy()
            path.append(name)
            newPath += name
            self.commandQ.put(cmd.Move(path, newPath))
        else:
            messagebox.showerror("Error", "New path cannot be empty")


    def rename(self, name, row, tmp):
        newName = simpledialog.askstring(title=name, prompt="Enter new name:", initialvalue=name)
        temp = self.current_path.copy()
        temp.append(newName)

        if newName is not None:
            path = self.current_path.copy()
            path.append(name)
            self.commandQ.put(cmd.Rename(path, temp))
        else:
            messagebox.showerror("Error", "New name cannot be null")


    def details(self, name):
        path = self.current_path.copy()
        path.append(name)
        self.commandQ.put(cmd.GetData(path))


    def uploadFile(self):
        file = filedialog.askopenfilename()
        if file != "":
            self.commandQ.put(cmd.Upload(self.__path[1:len(self.__path)], file))
        else:
            messagebox.showerror("Error", "File cannot be null")
    def makeDirectory(self):
        name = simpledialog.askstring(title="New folder/directory", prompt="Enter name: ")
        if name is not None:
            directory = self.current_path.copy()
            directory = directory[1:len(directory)]
            directory.append(name)
            self.commandQ.put(cmd.Create(directory))
        else:
            messagebox.showwarning("Warning", "Folder/Directory name cannot be empty")
    def setPort(self):
        comm.serverPort = self.__portVariable.get()

    def setIp(self):
        comm.serverIpAddress = self.__ipVariable.get()

    def backward(self):
        if len(self.__path) != 1:
            self.commandQ.put(cmd.ListDirectory(self.current_path[0:len(self.current_path) - 1]))


    def setType(self):
        print(self.__commTypeVariable.get())
        comm.CommunicationType = self.__commTypeVariable.get()

    def Refresh(self):
        """Refresh"""
        print('\ninterface, Refresh')
        self.commmandQ.put(cmd.ListDirectory(self.current_path))

    def EventListener(self):
        print('\ninterface, EventListener')
        while True:
            event: events.Event = self.eventQ.get()

