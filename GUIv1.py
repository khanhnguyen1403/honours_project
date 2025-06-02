import customtkinter as ctk
import tkinter as tk
import platform
import numpy as np
import random
import time
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime

# A scrollable grid frame to support many appliance cards in a neat layout
import tkinter as tk
import customtkinter as ctk
import platform

class ScrollableGrid(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, bg="#242424", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)

        # Inner frame where content lives
        self.inner_frame = ctk.CTkFrame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind resizing and scrolling
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Call the scroll binding method (this is what was missing)
        self._bind_scroll_events()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        # If the mouse is hovering over the Matplotlib canvas, ignore the scroll.
        if widget_under_cursor is not None and "canvas" in str(widget_under_cursor).lower():
            return

        # Otherwise, scroll the page
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(-1 * (event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def _bind_scroll_events(self):
        # Enable scroll wheel on all OS
        if platform.system() in ['Windows', 'Darwin']:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)

# Main application class
class App:
    def __init__(self, root, appliances):
        self.root = root
        self.root.title("DC Nanogrid Energy Management System")
        self.root.geometry("800x480")
        self.root.resizable(False, False)

        # Dark theme for aesthetics
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Time tracking and data containers
        self.start_time = time.time()
        self.time_data = deque(maxlen=200)
        self.appliances = appliances
        self.signal_data = {appliance: deque(maxlen=200) for appliance in appliances}
        self.data_buffer = {appliance: random.uniform(30, 500) for appliance in appliances}

        # Store Matplotlib elements and labels for updates
        self.signal_lines = {}
        self.signal_axes = {}
        self.manual_zoom = {appliance: False for appliance in self.appliances}
        self.total_manual_zoom = False
        self.signal_figs = {}
        self.appliance_value_labels = {}
        self.total_value_label = None

        # Set up tabs
        self.tabview = ctk.CTkTabview(self.root, width=800, height=480)
        self.tabview.pack(fill="both", expand=True)
        self.total_tab = self.tabview.add("Summary")
        self.appliances_tab = self.tabview.add("Details")
        self.log_tab = self.tabview.add("Logs")
        self.log_frame = ctk.CTkFrame(self.log_tab, corner_radius=0, fg_color="#222222")
        self.log_frame.pack(fill="both", expand=True)
        self.log_textbox = tk.Text(self.log_frame, bg="#1e1e1e", fg="white", insertbackground="white",
                           wrap="word", state="disabled")
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Total frame
        self.total_frame = ctk.CTkFrame(self.total_tab, width=800, height=480, corner_radius=0, fg_color="#222222")
        self.total_frame.pack(fill="both", expand=True)

        self.total_label = ctk.CTkLabel(self.total_frame, text="Total Power Consumption [W]",
                                        font=("Arial", 14, "bold"), anchor="w")
        self.total_label.place(x=10, y=10)

        self.plot_total_graph()  # Create summary plot

        # Toggle state for appliances
        self.state = {appliance: True for appliance in appliances}
        self.prev_state = {appliance: True for appliance in self.appliances} 
        self.buttons = {}

        # Protection
        self.protection_state = {appliance: False for appliance in appliances}

        # Track restart attempts and time for each appliance
        self.restart_attempts = {appliance: 0 for appliance in appliances}
        self.last_restart_time = {appliance: time.time() for appliance in appliances}

        # Scrollable grid of appliance plots
        self.grid_frame = ScrollableGrid(self.appliances_tab)
        self.grid_frame.pack(fill="both", expand=True)
        self.create_appliance_grid()

        self.log_event("Application successfully started.")

        # Periodic updates
        self.root.after(1000, self.generate_new_values)  # Every 1s: simulate data
        self.root.after(1000, self.update_graphs)        # Every 1s: update graphs

        # Zoom functionality for total graph
        self.total_fig.canvas.mpl_connect("scroll_event", lambda event: self.zoom(event, self.total_ax, self.total_fig))

        # Bind zoom functionality to appliance graphs
        self.drag_start_x = None
        for appliance in self.appliances:
            fig = self.signal_figs[appliance]
            ax = self.signal_axes[appliance]
            fig.canvas.mpl_connect("scroll_event", lambda event, ax=ax, fig=fig: self.zoom(event, ax, fig))

    def log_event(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}\n"
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", entry)
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def plot_total_graph(self):
        # Set up Matplotlib figure for total power
        fig = Figure(figsize=(8, 4.8), dpi=100)
        ax = fig.add_subplot(111)
        line, = ax.plot([], [], color='cyan', linewidth=2)

        # Style the axes
        ax.set_xlabel('Time [s]', color='white')
        ax.set_ylabel('Power [W]', color='white')
        ax.grid(True, color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_xlim(0,100)
        ax.set_ylim(0, 6000)
        ax.set_facecolor("#222222")
        fig.patch.set_facecolor("#222222")

        # Embed figure into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.total_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=(40, 10), expand=True)

        # Live power label
        self.total_value_label = ctk.CTkLabel(self.total_frame,
                                              text="Current Power: 0.00 W",
                                              font=("Arial", 12, "bold"),
                                              text_color="white",
                                              anchor="e")
        self.total_value_label.place(relx=0.98, y=10, anchor="ne")

        # Store references
        self.total_line = line
        self.total_ax = ax
        self.total_fig = fig

        canvas.mpl_connect("scroll_event", lambda event: self.zoom(event, ax, fig))
        canvas.mpl_connect("button_press_event", lambda event: self.on_press(event, ax, fig))
        canvas.mpl_connect("motion_notify_event", lambda event: self.on_drag(event, ax, fig))
        canvas.mpl_connect("button_release_event", lambda event: self.on_release(event, ax, fig))

    def create_appliance_grid(self):
        # Layout configuration for 2-column grid
        cols = 2
        box_width = 395
        box_height = 235

        # Create frames for each appliance
        for index, appliance_name in enumerate(self.appliances):
            row = index // cols
            col = index % cols

            frame = ctk.CTkFrame(self.grid_frame.inner_frame, width=box_width, height=box_height,
                                 corner_radius=0, fg_color="#333333", border_width=0, border_color="#555")
            frame.grid(row=row, column=col, padx=5, pady=5)
            frame.grid_propagate(False)

            # Appliance name label
            label = ctk.CTkLabel(frame, text=appliance_name, anchor="w",
                                 font=("Arial", 14, "bold"), text_color="white")
            label.place(x=10, y=10)

            # Add plot to frame
            self.init_appliance_graph(frame, appliance_name)

            # Toggle button
            button = ctk.CTkButton(
                frame, text="ON", width=60,
                fg_color="green", hover_color="#006400",
                font=("Arial", 11, "bold"),
                command=lambda name=appliance_name, btn=frame: self.toggle_appliance(name)
            )
            button.place (x = 150, y = 10)
            frame.button = button 
            self.buttons[appliance_name] = button

    def toggle_appliance(self, name):
        # Flip toggle state
        self.state[name] = not self.state[name]

        btn = self.buttons[name]
        if self.state[name]:
            btn.configure(text="ON", fg_color="green", hover_color="#006400")
            self.log_event(f"{name} turned ON.")
        else:
            btn.configure(text="OFF", fg_color="red", hover_color="#8B0000")
            self.log_event(f"{name} turned OFF.")

    def init_appliance_graph(self, parent_frame, appliance_name):
        fig = Figure(figsize=(3.8, 1.8), dpi=100)
        ax = fig.add_subplot(111)
        line, = ax.plot([], [], color='orange', linewidth=1.5)

        ax.set_xlabel('Time [s]', color='white')
        ax.set_ylabel('Power [W]', color='white')
        ax.grid(True, color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 600)
        ax.set_facecolor("#333333")
        fig.patch.set_facecolor("#333333")
        fig.subplots_adjust(left=0.18, right=0.95, top=0.90, bottom=0.25)

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=(70, 20), expand=True)

        # Current value label
        value_label = ctk.CTkLabel(parent_frame,
                                   text="Current Power: 0.00 W",
                                   font=("Arial", 11, "bold"),
                                   text_color="white",
                                   anchor="e")
        value_label.place(relx=0.98, y=10, anchor="ne")

        # Store references
        self.appliance_value_labels[appliance_name] = value_label
        self.signal_lines[appliance_name] = line
        self.signal_axes[appliance_name] = ax
        self.signal_figs[appliance_name] = fig

        # Bind zoom functionality
        canvas.mpl_connect("scroll_event", lambda event, app_name=appliance_name, axis=ax, fig=fig: self.zoom(event, ax, fig, appliance_name))
        canvas.mpl_connect("button_press_event", lambda event, app_name=appliance_name, axis=ax, fig=fig: self.on_press(event, ax, fig, appliance_name))
        canvas.mpl_connect("motion_notify_event", lambda event, app_name=appliance_name, axis=ax, fig=fig: self.on_drag(event, ax, fig, appliance_name))
        canvas.mpl_connect("button_release_event", lambda event, app_name=appliance_name, axis=ax, fig=fig: self.on_release(event, ax, fig, appliance_name))
        
    def generate_new_values(self):
        # Simulate new power readings every second
        for appliance in self.appliances:
            if self.state[appliance] and not self.prev_state[appliance]: # just turned on
                new_value = random.uniform(30, 500)
            elif self.state[appliance]: # still on
                prev_value = self.signal_data[appliance][-1] if self.signal_data[appliance] else random.uniform(30, 500)
                delta = random.uniform(-10, 10)
                if delta >= prev_value:
                    delta = 0
                new_value = prev_value + delta
            else: # off
                new_value = 0
            self.data_buffer[appliance] = new_value # save value

            # Update previous state
            self.prev_state[appliance] = self.state[appliance]
            
        self.root.after(1000, self.generate_new_values)

    def protection(self, appliance):
        power = self.data_buffer[appliance]
        if power > 700 and self.state[appliance] and not self.protection_state[appliance]:
            self.protection_state[appliance] = True
            self.toggle_appliance(appliance) # turn off appliance
            self.log_event(f"{appliance}: Overload detected. Power: {power:.2f} W")

        if power < 0 and self.state[appliance] and not self.protection_state[appliance]:
            self.protection_state[appliance] = True
            self.toggle_appliance(appliance) # turn off appliance
            self.log_event(f"{appliance}: Reverse Current flow detected.")
            self.root.after(2000, lambda:self.auto_restart(appliance))

    def auto_restart(self, appliance):
        current_time = time.time()
        
        # Check if the 10-second window has passed
        if current_time - self.last_restart_time[appliance] > 10:
            # Reset the restart attempt counter
            self.restart_attempts[appliance] = 0
            self.last_restart_time[appliance] = current_time

        # If the appliance has had fewer than 2 restart attempts in the last 10 seconds
        if self.restart_attempts[appliance] < 1:
            # Proceed with the auto-restart
            self.restart_attempts[appliance] += 1
            self.state[appliance] = True
            self.buttons[appliance].configure(text="ON", fg_color="green", hover_color="#006400")
            self.log_event(f"{appliance}: Auto restart initiated.")
        else:
            # If there have been 2 attempts already, lock auto restart
            self.log_event(f"{appliance}: Auto restart locked out.")
        self.protection_state[appliance] = False

    def update_graphs(self):
        # Update all plots with the new data
        now = time.time() - self.start_time
        self.time_data.append(now)

        for appliance in self.appliances:
            new_value = self.data_buffer[appliance]
            self.signal_data[appliance].append(new_value)

            # Update graph line
            line = self.signal_lines[appliance]
            ax = self.signal_axes[appliance]
            line.set_data(self.time_data, self.signal_data[appliance])
            if not self.manual_zoom[appliance]:
                if now < 8:
                    ax.set_xlim(0, 10)
                else:
                    ax.set_xlim(max(0, now - 8), now + 2)
            ax.set_ylim(0, 600)
            self.signal_figs[appliance].canvas.draw()

            # Update label
            self.appliance_value_labels[appliance].configure(
                text=f"Current Power: {new_value:.2f} W"
            )
            self.protection(appliance) # check for potential issues

        # Total power calculation and update
        total_y = np.sum([self.signal_data[appliance] for appliance in self.appliances], axis=0)
        self.total_line.set_data(self.time_data, total_y)
        if not self.total_manual_zoom:
            if now < 80:
                self.total_ax.set_xlim(0, 100)
            else:
                self.total_ax.set_xlim(max(0, now - 80), now + 20)
        self.total_ax.set_ylim(0, 6000)
        self.total_fig.canvas.draw()

        if len(total_y) > 0:
            self.total_value_label.configure(text=f"Current Power: {total_y[-1]:.2f} W")

        self.root.after(1000, self.update_graphs)


    def zoom(self, event, ax, fig, appliance_name=None):
        base_scale = 1.1
        x_min, x_max = ax.get_xlim()
        x_range = (x_max - x_min)

        # Determine zoom direction
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        # Get mouse position in x data coords
        mouse_x = event.xdata
        if mouse_x is None:
            return  # Ignore if outside plot area

        # New x-axis limits
        new_x_min = mouse_x - (mouse_x - x_min) * scale_factor
        new_x_max = mouse_x + (x_max - mouse_x) * scale_factor

        # Clamp: prevent over-zoom or ridiculous range
        min_range = 1.0
        max_range = 1000.0
        new_range = new_x_max - new_x_min
        if new_range < min_range or new_range > max_range:
            return

        ax.set_xlim(max(0,new_x_min), new_x_max)
        fig.canvas.draw()

        if appliance_name is None:
            # Zoom on total plot
            self.total_manual_zoom = True
        else:
            # Zoom on a specific appliance
            self.manual_zoom[appliance_name] = True

    def on_press(self, event, ax, fig, appliance_name=None):
        if event.button == 1 and event.inaxes is not None:  # Left click inside axes
            self.drag_start_x = event.xdata
            self.active_ax = event.inaxes
            if appliance_name is None:
                # Zoom on total plot
                self.total_manual_zoom = True
            else:
                # Zoom on a specific appliance
                self.manual_zoom[appliance_name] = True 

        if event.button == 3 and event.inaxes is not None: # right click
            # Reset zoom to default limits
            now = time.time() - self.start_time
            if appliance_name is None:
                self.total_manual_zoom = False
                if now < 80:
                    self.total_ax.set_xlim(0, 100)
                else:
                    self.total_ax.set_xlim(max(0, now - 80), now + 20)
            else:
                self.manual_zoom[appliance_name] = False
                if now < 8:
                    ax.set_xlim(0, 10)
                else:
                    ax.set_xlim(max(0, now - 8), now + 2)
            self.update_graphs()  # Update the graph to reflect the reset
            fig.canvas.draw()

    def on_drag(self, event, ax, fig, appliance_name=None):
        if (
            self.drag_start_x is None
            or event.xdata is None
            or event.inaxes != self.active_ax 
        ):
            return

        dx = event.xdata - self.drag_start_x
        cur_xlim = ax.get_xlim()
        ax.set_xlim(max(0,cur_xlim[0] - dx), cur_xlim[1] - dx)
        self.drag_start_x = event.xdata
        event.canvas.draw()

        if appliance_name is None:
            # Zoom on total plot
            self.total_manual_zoom = True
        else:
            # Zoom on a specific appliance
            self.manual_zoom[appliance_name] = True 

    def on_release(self, event, ax, fig, appliance_name=None):
        if event.button == 1:
            self.drag_start_x = None
            self.active_ax = None 


# Run the app
if __name__ == "__main__":
    appliances = [
        "Dishwasher", "Air Conditioner", "Induction Cooktop", "Lights",
        "Oven", "Microwave", "Washing Machine", "Dryer",
        "Fan", "Heater", "Fridge"
    ]

    root = tk.Tk()
    app = App(root, appliances)
    root.mainloop()
