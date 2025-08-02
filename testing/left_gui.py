from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import datetime


class Left_GUI:
    def __init__ (self, root, data):
        self.root = root
        self.data = data 

        self.addFrame()
        self.addGraph(data)
        
    def addFrame(self):
        self.frame_graph = LabelFrame(self.root, text="Display",
                            padx=5, pady=5, bg="white")
        self.frame_graph.grid(row=4, column=0, columnspan=6, padx=5, pady=3, sticky='nsew')

        self.frame_stats = LabelFrame(self.root, text="Properties",
                            padx=5, pady=0, bg="white")
        self.frame_stats.grid(row=6, column=0, rowspan=3, columnspan=6, padx=5, pady=3, sticky='nsew')

        # Configure row and column weights for proper alignment
        self.frame_stats.grid_rowconfigure(0, weight=1)
        self.frame_stats.grid_columnconfigure(0, weight=1)
        self.frame_stats.grid_columnconfigure(3, weight=1)

        self.label_stats1 = Label(self.frame_stats, text="Power:", bg="white")
        self.label_stats2 = Label(self.frame_stats, text="Voltage:", bg="white")
        self.label_stats3 = Label(self.frame_stats, text="Current:", bg="white")
        self.label_stats4 = Label(self.frame_stats, text="Energy used:", bg="white")
        self.label_stats5 = Label(self.frame_stats, text="Time operated:", bg="white")
        self.label_stats6 = Label(self.frame_stats, text="Fault:", bg="white")

        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=1, column=0, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=2, column=0, padx=5, pady=3, sticky='w')
        self.label_stats4.grid(row=0, column=3, padx=5, pady=3, sticky="w") 
        self.label_stats5.grid(row=1, column=3, padx=5, pady=3, sticky="w")
        self.label_stats6.grid(row=2, column=3, padx=5, pady=3, sticky="w") 

        self.label_stats1_value = Label(self.frame_stats, text="0 W", bg="white")
        self.label_stats2_value = Label(self.frame_stats, text="0 V", bg="white")
        self.label_stats3_value = Label(self.frame_stats, text="0 A", bg="white")
        self.label_stats4_value = Label(self.frame_stats, text="0 kWh", bg="white")
        self.label_stats5_value = Label(self.frame_stats, text="0 min", bg="white")
        self.label_stats6_value = Label(self.frame_stats, text="No Fault", bg="white") 

        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=1, column=1, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=2, column=1, padx=5, pady=3, sticky='e')
        self.label_stats4_value.grid(row=0, column=5, padx=5, pady=3, sticky="e") 
        self.label_stats5_value.grid(row=1, column=5, padx=5, pady=3, sticky="e")
        self.label_stats6_value.grid(row=2, column=5, padx=5, pady=3, sticky="e")

    def addGraph(self,data):
        self.fig = plt.Figure(figsize=(5,3), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(data, label='Data Plot')
        self.ax.grid(True) 
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas.get_tk_widget().grid(
            column=1, row=0, columnspan=3, sticky=N)
 