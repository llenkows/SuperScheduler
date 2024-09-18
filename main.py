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

        # Create buttons for adding, editing, and removing tasks
        self.add_button = tk.Button(self.top, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.edit_button = tk.Button(self.top, text="Edit Task", command=self.edit_task)
        self.edit_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.remove_button = tk.Button(self.top, text="Remove Task", command=self.remove_task)
        self.remove_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Load tasks into the listbox
        self.load_tasks()

    def load_tasks(self):
        self.task_list.delete(0, tk.END)
        if self.date_key in self.calendar_app.tasks:
            tasks = self.calendar_app.tasks[self.date_key]
            for index, task in enumerate(tasks):
                if isinstance(task, dict):  # Ensure task is a dictionary
                    task_info = f"{index + 1}. {task['name']} - {task['category']} - {task['status']} - Due: {task.get('due_time', 'No Time')}"
                    self.task_list.insert(tk.END, task_info)

    def add_task(self):
        # Create a single window for task addition
        add_task_window = tk.Toplevel(self.top)
        add_task_window.title("Add Task")
        add_task_window.geometry("400x400")  # Adjust the window size to fit all elements

        # Task Name
        tk.Label(add_task_window, text="Task Name:").pack(pady=5)
        task_name_var = tk.StringVar()
        task_name_entry = tk.Entry(add_task_window, textvariable=task_name_var)
        task_name_entry.pack(pady=5)

        # Task Category
        tk.Label(add_task_window, text="Category:").pack(pady=5)
        category_var = tk.StringVar()
        category_entry = tk.Entry(add_task_window, textvariable=category_var)
        category_entry.pack(pady=5)

        # Time Input (Hour, Minute, AM/PM)
        tk.Label(add_task_window, text="Select Time:").pack(pady=5)

        hour_var = tk.IntVar(value=12)
        minute_var = tk.IntVar(value=0)
        am_pm_var = tk.StringVar(value="AM")

        time_frame = tk.Frame(add_task_window)
        time_frame.pack(pady=5)

        tk.Label(time_frame, text="Hour (1-12):").pack(side=tk.LEFT, padx=5)
        hour_spinbox = tk.Spinbox(time_frame, from_=1, to=12, textvariable=hour_var, width=5)
        hour_spinbox.pack(side=tk.LEFT, padx=5)

        tk.Label(time_frame, text="Minute (0-59):").pack(side=tk.LEFT, padx=5)
        minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=5)
        minute_spinbox.pack(side=tk.LEFT, padx=5)

        am_pm_frame = tk.Frame(add_task_window)
        am_pm_frame.pack(pady=5)
        tk.Radiobutton(am_pm_frame, text="AM", variable=am_pm_var, value="AM").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(am_pm_frame, text="PM", variable=am_pm_var, value="PM").pack(side=tk.LEFT, padx=5)

        # Task Status Selection
        tk.Label(add_task_window, text="Task Status:").pack(pady=10)

        status_var = tk.StringVar(value="Unfinished")

        status_frame = tk.Frame(add_task_window)
        status_frame.pack(pady=5)
        tk.Radiobutton(status_frame, text="Unfinished", variable=status_var, value="Unfinished").pack(anchor=tk.W)
        tk.Radiobutton(status_frame, text="Work in Progress", variable=status_var, value="Work in Progress").pack(anchor=tk.W)
        tk.Radiobutton(status_frame, text="Completed", variable=status_var, value="Completed").pack(anchor=tk.W)

        # Confirm Button
        def confirm_add_task():
            task_name = task_name_var.get()
            category = category_var.get()
            status = status_var.get()

            if not task_name or not category:
                messagebox.showerror("Error", "Task name and category cannot be empty!")
                return

            hour = hour_var.get()
            minute = minute_var.get()
            am_pm = am_pm_var.get()

            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0

            due_time = f"{hour % 12 or 12}:{minute:02d} {am_pm}"

            new_task = {
                "name": task_name,
                "category": category,
                "status": status,
                "due_time": due_time
            }

            if self.date_key not in self.calendar_app.tasks:
                self.calendar_app.tasks[self.date_key] = []

            self.calendar_app.tasks[self.date_key].append(new_task)
            self.calendar_app.save_tasks()
            self.load_tasks()
            self.calendar_app.show_calendar(self.year, self.month)
            add_task_window.destroy()

        confirm_button = tk.Button(add_task_window, text="Add Task", command=confirm_add_task)
        confirm_button.pack(pady=20)

    def edit_task(self):
        selected_index = self.task_list.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return

        task_index = selected_index[0]
        task = self.calendar_app.tasks[self.date_key][task_index]

        edit_task_window = tk.Toplevel(self.top)
        edit_task_window.title("Edit Task")
        edit_task_window.geometry("400x400")

        # Task Name
        tk.Label(edit_task_window, text="Task Name:").pack(pady=5)
        task_name_var = tk.StringVar(value=task['name'])
        task_name_entry = tk.Entry(edit_task_window, textvariable=task_name_var)
        task_name_entry.pack(pady=5)

        # Task Category
        tk.Label(edit_task_window, text="Category:").pack(pady=5)
        category_var = tk.StringVar(value=task['category'])
        category_entry = tk.Entry(edit_task_window, textvariable=category_var)
        category_entry.pack(pady=5)

        # Time Input (Hour, Minute, AM/PM)
        tk.Label(edit_task_window, text="Select Time:").pack(pady=5)

        hour_var = tk.IntVar(value=int(task['due_time'].split(':')[0]))
        minute_var = tk.IntVar(value=int(task['due_time'].split(':')[1].split()[0]))
        am_pm_var = tk.StringVar(value=task['due_time'].split()[-1])

        time_frame = tk.Frame(edit_task_window)
        time_frame.pack(pady=5)

        tk.Label(time_frame, text="Hour (1-12):").pack(side=tk.LEFT, padx=5)
        hour_spinbox = tk.Spinbox(time_frame, from_=1, to=12, textvariable=hour_var, width=5)
        hour_spinbox.pack(side=tk.LEFT, padx=5)

        tk.Label(time_frame, text="Minute (0-59):").pack(side=tk.LEFT, padx=5)
        minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=5)
        minute_spinbox.pack(side=tk.LEFT, padx=5)

        am_pm_frame = tk.Frame(edit_task_window)
        am_pm_frame.pack(pady=5)
        tk.Radiobutton(am_pm_frame, text="AM", variable=am_pm_var, value="AM").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(am_pm_frame, text="PM", variable=am_pm_var, value="PM").pack(side=tk.LEFT, padx=5)

        # Task Status Selection
        tk.Label(edit_task_window, text="Task Status:").pack(pady=10)

        status_var = tk.StringVar(value=task['status'])

        status_frame = tk.Frame(edit_task_window)
        status_frame.pack(pady=5)
        tk.Radiobutton(status_frame, text="Unfinished", variable=status_var, value="Unfinished").pack(anchor=tk.W)
        tk.Radiobutton(status_frame, text="Work in Progress", variable=status_var, value="Work in Progress").pack(anchor=tk.W)
        tk.Radiobutton(status_frame, text="Completed", variable=status_var, value="Completed").pack(anchor=tk.W)

        # Confirm Button
        def confirm_edit_task():
            task_name = task_name_var.get()
            category = category_var.get()
            status = status_var.get()

            if not task_name or not category:
                messagebox.showerror("Error", "Task name and category cannot be empty!")
                return

            hour = hour_var.get()
            minute = minute_var.get()
            am_pm = am_pm_var.get()

            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0

            due_time = f"{hour % 12 or 12}:{minute:02d} {am_pm}"

            updated_task = {
                "name": task_name,
                "category": category,
                "status": status,
                "due_time": due_time
            }

            self.calendar_app.tasks[self.date_key][task_index] = updated_task
            self.calendar_app.save_tasks()
            self.load_tasks()
            self.calendar_app.show_calendar(self.year, self.month)
            edit_task_window.destroy()

        confirm_button = tk.Button(edit_task_window, text="Save Changes", command=confirm_edit_task)
        confirm_button.pack(pady=20)

    def remove_task(self):
        selected_index = self.task_list.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to remove.")
            return

        task_index = selected_index[0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            del self.calendar_app.tasks[self.date_key][task_index]
            self.calendar_app.save_tasks()
            self.load_tasks()
            self.calendar_app.show_calendar(self.year, self.month)

# Initialize the Tkinter app
root = tk.Tk()
app = TaskCalendar(root)
root.mainloop()
