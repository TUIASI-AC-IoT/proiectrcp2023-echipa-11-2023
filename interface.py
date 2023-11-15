


# imports
import tkinter as tk

# Window Class
class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        """To be updated in the future"""
        self.geometry("800x200")
        self.grid()


        # menu frame
        self.__menu = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        self.__menu.grid()
        self.__menu.pack(anchor="n", fill="x")


        # button for connection type

        """To do: add command"""
        self.__commTypeVariable = tk.IntVar()
        self.__commType = tk.Checkbutton(self.__menu, text="Non-Confirmable", command=None, variable=self.__commTypeVariable)
        self.__commType.grid(column=0, row=0)

        # ip display
        self.__ipVariable = tk.StringVar()
        self.__ip = tk.Entry(self.__menu, textvariable=self.__ipVariable)
        self.__ip.config(width=12)
        self.__ip.grid(column=1, row=0)

        # port display
        self.__portVariable = tk.IntVar()
        self.__port = tk.Entry(self.__menu)
        self.__port.configure(width=10)
        self.__port.grid(column=2, row=0)

        # backward button
        """To do: add command"""
        self.__back = tk.Button(self.__menu, text="<<", command=None)
        self.__back.grid(column=3, row=0)

        # refresh button
        """To do: add command"""
        self.__refresh = tk.Button(self.__menu, text="Refresh", command=None)
        self.__refresh.grid(column=4, row=0)

        # current path to directory
        self.__path = tk.Label(self.__menu, text="")
        self.__path.grid(column=5, row=0)

