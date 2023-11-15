


#imports
import tkinter as tk



#class definitions

class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("300x200")
        self.grid()


        #menu frame
        self.__menu = tk.Frame(self, highlightbackground="black", highlightthickness=1)
        self.__menu.grid()
        self.__menu.pack(anchor="n", fill="x")


