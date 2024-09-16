import tkinter as tk
from tkinter import simpledialog, messagebox
import calendar
from datetime import datetime
import json
import os

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

    def add_task(self, year, month, day):
        date_key = f"{year}-{month:02d}-{day:02d}"
        task_name = simpledialog.askstring("Task Name", "Enter the name of the task:")
        if not task_name:
            return

        category = simpledialog.askstring("Task Category", "Enter the task category:")
        if not category:
            messagebox.showerror("Error", "Category cannot be empty!")
            return

        # Open a new window to select the status
        status_window = tk.Toplevel(self.root)
        status_window.title("Select Task Status")
        status_window.geometry("300x150")

        status = tk.StringVar(value="")

        tk.Label(status_window, text="Select the task status:", font=("Arial", 12)).pack(pady=10)

        # Create buttons for status selection
        tk.Button(status_window, text="Unfinished", command=lambda: self.set_status(status, "Unfinished", status_window)).pack(pady=5, fill=tk.X)
        tk.Button(status_window, text="Work in Progress", command=lambda: self.set_status(status, "Work in Progress", status_window)).pack(pady=5, fill=tk.X)
        tk.Button(status_window, text="Complete", command=lambda: self.set_status(status, "Complete", status_window)).pack(pady=5, fill=tk.X)

        self.root.wait_window(status_window)  # Wait for the status window to close

        if not status.get():
            messagebox.showerror("Error", "Status cannot be empty!")
            return

        if date_key not in self.tasks:
            self.tasks[date_key] = []
        self.tasks[date_key].append({"name": task_name, "category": category, "status": status.get()})
        self.save_tasks()

        self.show_calendar(self.current_year, self.current_month)

    def set_status(self, status_var, status_value, window):
        status_var.set(status_value)
        window.destroy()

class TaskWindow:
    def __init__(self, parent, year, month, day, calendar_app):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Tasks for {day}/{month}/{year}")

        self.calendar_app = calendar_app
        self.year = year
        self.month = month
        self.day = day
        self.date_key = f"{year}-{month:02d}-{day:02d}"

        # Create a frame for the tasks list
        self.task_frame = tk.Frame(self.top)
        self.task_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Create a scrollbar for the task list
        self.scroll_y = tk.Scrollbar(self.task_frame, orient="vertical")
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_list = tk.Listbox(self.task_frame, yscrollcommand=self.scroll_y.set, selectmode=tk.SINGLE)
        self.task_list.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.scroll_y.config(command=self.task_list.yview)

        # Create buttons for adding and removing tasks
        self.add_button = tk.Button(self.top, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.remove_button = tk.Button(self.top, text="Remove Task", command=self.remove_task)
        self.remove_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.update_button = tk.Button(self.top, text="Update Task Status", command=self.update_task_status)
        self.update_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Load tasks into the listbox
        self.load_tasks()

    def load_tasks(self):
        self.task_list.delete(0, tk.END)
        if self.date_key in self.calendar_app.tasks:
            tasks = self.calendar_app.tasks[self.date_key]
            for index, task in enumerate(tasks):
                if isinstance(task, dict):  # Ensure task is a dictionary
                    task_info = f"{index + 1}. {task['name']} - {task['category']} - {task['status']}"
                    self.task_list.insert(tk.END, task_info)

    def add_task(self):
        task_name = simpledialog.askstring("Task Name", "Enter the name of the task:")
        if not task_name:
            return

        category = simpledialog.askstring("Task Category", "Enter the task category:")
        if not category:
            messagebox.showerror("Error", "Category cannot be empty!")
            return

        # Open a new window to select the status
        status_window = tk.Toplevel(self.top)
        status_window.title("Select Task Status")
        status_window.geometry("300x150")

        status = tk.StringVar(value="")

        tk.Label(status_window, text="Select the task status:", font=("Arial", 12)).pack(pady=10)

        # Create buttons for status selection
        tk.Button(status_window, text="Unfinished", command=lambda: self.set_status(status, "Unfinished", status_window)).pack(pady=5, fill=tk.X)
        tk.Button(status_window, text="Work in Progress", command=lambda: self.set_status(status, "Work in Progress", status_window)).pack(pady=5, fill=tk.X)
        tk.Button(status_window, text="Complete", command=lambda: self.set_status(status, "Complete", status_window)).pack(pady=5, fill=tk.X)

        self.top.wait_window(status_window)  # Wait for the status window to close

        if not status.get():
            messagebox.showerror("Error", "Status cannot be empty!")
            return

        new_task = {"name": task_name, "category": category, "status": status.get()}
        if self.date_key not in self.calendar_app.tasks:
            self.calendar_app.tasks[self.date_key] = []  # Initialize as an empty list

        self.calendar_app.tasks[self.date_key].append(new_task)
        self.calendar_app.save_tasks()
        self.load_tasks()

    def set_status(self, status_var, status_value, window):
        status_var.set(status_value)
        window.destroy()

    def remove_task(self):
        selected_index = self.task_list.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No task selected!")
            return

        task_index = selected_index[0]

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to remove this task?"):
            del self.calendar_app.tasks[self.date_key][task_index]
            if not self.calendar_app.tasks[self.date_key]:
                del self.calendar_app.tasks[self.date_key]
            self.calendar_app.save_tasks()
            self.load_tasks()

    def update_task_status(self):
        selected_index = self.task_list.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No task selected!")
            return

        task_index = selected_index[0]

        # Open a new window to select the new status
        status_window = tk.Toplevel(self.top)
        status_window.title("Select New Task Status")
        status_window.geometry("300x150")

        status = tk.StringVar(value="")

        tk.Label(status_window, text="Select the new status:", font=("Arial", 12)).pack(pady=10)

        # Create buttons for status selection
        tk.Button(status_window, text="Unfinished", command=lambda: self.set_status(status, "Unfinished", status_window)).pack(pady=5, fill=tk.X)
        tk.Button(status_window, text="Work in Progress", command=lambda: self.set_status(status, "Work in Progress", status_window)).pack(pady=5, fill=tk.X)
        tk.Button(status_window, text="Complete", command=lambda: self.set_status(status, "Complete", status_window)).pack(pady=5, fill=tk.X)

        self.top.wait_window(status_window)  # Wait for the status window to close

        if not status.get():
            messagebox.showerror("Error", "Status cannot be empty!")
            return

        self.calendar_app.tasks[self.date_key][task_index]['status'] = status.get()
        self.calendar_app.save_tasks()
        self.load_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskCalendar(root)
    root.mainloop()
