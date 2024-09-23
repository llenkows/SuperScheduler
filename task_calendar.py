import os, json, calendar, threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from task_window import TaskWindow
from pystray import Icon, MenuItem as item
from PIL import Image

# File to store tasks
TASKS_FILE = 'tasks.json'


class TaskCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Calendar")

        # Set a larger initial window size
        self.root.geometry("900x600")
        self.root.minsize(800, 600)

        self.tasks = self.load_tasks()

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        # Store button references in a dictionary
        self.date_buttons = {}

        # Create a frame for navigation and label
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(fill=tk.X, pady=10)

        self.prev_button = tk.Button(self.nav_frame, text="<< Previous", command=self.prev_month)
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.label = tk.Label(self.nav_frame, text="", font=("Arial", 16), anchor="center")
        self.label.pack(side=tk.LEFT, expand=True)

        self.next_button = tk.Button(self.nav_frame, text="Next >>", command=self.next_month)
        self.next_button.pack(side=tk.RIGHT, padx=10)

        # Create a frame for the calendar
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH)

        # Configure dynamic resizing of the calendar frame
        for i in range(7):  # 7 columns for the days of the week
            self.calendar_frame.grid_columnconfigure(i, weight=1, uniform="day")
        self.root.grid_rowconfigure(1, weight=1)  # Make the calendar area expandable

        self.show_calendar(self.current_year, self.current_month)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def reset_application(self):
        """Reset the application state and reload everything."""
        self.tasks = self.load_tasks()
        self.show_calendar(self.current_year, self.current_month)

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_tasks(self):
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=4)

    def show_calendar(self, year, month):
        # Clear previous widgets in the calendar frame
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Clear the date_buttons dictionary
        self.date_buttons.clear()

        # Update the label with the current month and year
        self.label.config(text=f"{calendar.month_name[month]} {year}")

        cal = calendar.Calendar(firstweekday=0)
        days = cal.itermonthdays(year, month)

        row, col = 0, 0
        # Add day headers (Mon, Tue, etc.)
        headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in headers:
            header_label = tk.Label(self.calendar_frame, text=day, font=("Arial", 12, "bold"), padx=10, pady=5)
            header_label.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            col += 1

        row += 1
        col = 0

        # Create buttons for each day of the current month
        for day in days:
            if day == 0:
                col += 1
                if col > 6:
                    col = 0
                    row += 1
                continue

            date_key = f"{year}-{month:02d}-{day:02d}"
            has_tasks = date_key in self.tasks and len(self.tasks[date_key]) > 0

            # Create a button for the day number
            day_button = tk.Button(
                self.calendar_frame, text=str(day), width=5, height=2,
                bg="lightgrey" if has_tasks else "white",
                command=lambda d=day, y=year, m=month: self.open_task_window(y, m, d)
            )
            day_button.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

            # Store the button in the date_buttons dictionary
            self.date_buttons[date_key] = day_button

            col += 1
            if col > 6:
                col = 0
                row += 1

        # Adjust the grid row configuration so that rows grow proportionally with window resizing
        for i in range(row + 1):
            self.calendar_frame.grid_rowconfigure(i, weight=1, uniform="day")

        # Update the colors of the date boxes based on task due dates
        self.update_date_boxes()

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.show_calendar(self.current_year, self.current_month)

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.show_calendar(self.current_year, self.current_month)

    def get_date_button(self, date_key):
        """Retrieve the button associated with a specific date."""
        return self.date_buttons.get(date_key)

    def update_date_boxes(self):
        """Update calendar date boxes based on the proximity of tasks' due dates."""
        today = datetime.today().date()

        for date_key, tasks in self.tasks.items():
            task_date = datetime.strptime(date_key, "%Y-%m-%d").date()

            # Find the corresponding button for the date
            date_button = self.get_date_button(date_key)

            if date_button:
                # Set colors based on how far the task is
                if task_date == today:
                    date_button.config(bg="orange")  # Task due today
                elif task_date == today + timedelta(days=1):
                    date_button.config(bg="yellow")  # Task due tomorrow
                elif task_date < today:
                    date_button.config(bg="red")  # Task past due
                else:
                    date_button.config(bg="lightgrey")  # No special color if it's beyond tomorrow

    def open_task_window(self, year, month, day):
        TaskWindow(self.root, year, month, day, self)

    def on_closing(self):
        response = messagebox.askyesnocancel("Exit", "Do you want to run the program in the background?")
        if response is None:  # User canceled
            return
        elif response:  # Yes - run in background
            self.root.withdraw()  # Hide the main window
            self.create_tray_icon()  # Start the tray icon
        else:  # No - close completely
            self.root.quit()

    def create_tray_icon(self):
        icon_image = Image.open("icon.png")
        menu = (item('Restore', self.restore), item('Exit', self.root.quit))
        tray_icon = Icon("SuperScheduler", icon_image, menu=menu)

        # Run the icon in a separate thread
        threading.Thread(target=tray_icon.run, args=(self.setup_tray,), daemon=True).start()

    def setup_tray(self, icon):
        icon.visible = True  # Make sure the icon is visible

    def restore(self):
        self.root.deiconify()  # Show the main window again
        self.root.lift()  # Bring the window to the front
        self.root.focus_force()  # Force focus on the window

        # Ensure the close protocol is set again
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Reset and reload everything
        self.reset_application()
