from tkinter import *

class RootGUI: 
    def __init__(self):
        self.root = Tk()
        self.root.title("DC Nanogrid Control Panel")
        self.root.geometry("800x480")
        self.root.resizable(False, False)
        self.root.config(bg="white")

        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(6, weight=2)