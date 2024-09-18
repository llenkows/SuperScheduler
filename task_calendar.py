import os
import json
import calendar
from datetime import datetime
import tkinter as tk
from task_window import TaskWindow

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

            col += 1
            if col > 6:
                col = 0
                row += 1

        # Adjust the grid row configuration so that rows grow proportionally with window resizing
        for i in range(row + 1):
            self.calendar_frame.grid_rowconfigure(i, weight=1, uniform="day")

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

    def open_task_window(self, year, month, day):
        TaskWindow(self.root, year, month, day, self)