import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# File to store tasks
TASKS_FILE = 'tasks.json'
class TaskWindow:
    def __init__(self, parent, year, month, day, calendar_app):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Tasks for {day}/{month}/{year}")

        # Increase the size of the task window
        self.top.geometry("500x400")
        self.top.minsize(400, 300)

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

        self.add_button = tk.Button(self.top, text="Add Recurring Task", command=self.add_recurring_tasks)
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

        # Increase the size of the add task window
        add_task_window.geometry("500x500")
        add_task_window.minsize(400, 400)

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
            self.calendar_app.show_calendar(self.calendar_app.current_year, self.calendar_app.current_month)
            add_task_window.destroy()

        confirm_button = tk.Button(add_task_window, text="Add Task", command=confirm_add_task)
        confirm_button.pack(pady=20)

    def add_recurring_tasks(self):
        # Create a window for recurring task addition
        recurring_task_window = tk.Toplevel(self.top)
        recurring_task_window.title("Add Recurring Task")

        # Adjust size
        recurring_task_window.geometry("500x600")
        recurring_task_window.minsize(400, 500)

        # Task Name
        tk.Label(recurring_task_window, text="Task Name:").pack(pady=5)
        task_name_var = tk.StringVar()
        task_name_entry = tk.Entry(recurring_task_window, textvariable=task_name_var)
        task_name_entry.pack(pady=5)

        # Task Category
        tk.Label(recurring_task_window, text="Category:").pack(pady=5)
        category_var = tk.StringVar()
        category_entry = tk.Entry(recurring_task_window, textvariable=category_var)
        category_entry.pack(pady=5)

        # Time Input (Hour, Minute, AM/PM)
        tk.Label(recurring_task_window, text="Select Time:").pack(pady=5)

        hour_var = tk.IntVar(value=12)
        minute_var = tk.IntVar(value=0)
        am_pm_var = tk.StringVar(value="AM")

        time_frame = tk.Frame(recurring_task_window)
        time_frame.pack(pady=5)

        tk.Label(time_frame, text="Hour (1-12):").pack(side=tk.LEFT, padx=5)
        hour_spinbox = tk.Spinbox(time_frame, from_=1, to=12, textvariable=hour_var, width=5)
        hour_spinbox.pack(side=tk.LEFT, padx=5)

        tk.Label(time_frame, text="Minute (0-59):").pack(side=tk.LEFT, padx=5)
        minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=5)
        minute_spinbox.pack(side=tk.LEFT, padx=5)

        am_pm_frame = tk.Frame(recurring_task_window)
        am_pm_frame.pack(pady=5)
        tk.Radiobutton(am_pm_frame, text="AM", variable=am_pm_var, value="AM").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(am_pm_frame, text="PM", variable=am_pm_var, value="PM").pack(side=tk.LEFT, padx=5)

        # Recurrence Options
        tk.Label(recurring_task_window, text="Recurrence:").pack(pady=10)

        recurrence_var = tk.StringVar(value="Daily")
        recurrence_options = ["Daily", "Every Other Day", "Weekly", "Every Other Week", "Monthly"]

        recurrence_menu = tk.OptionMenu(recurring_task_window, recurrence_var, *recurrence_options)
        recurrence_menu.pack(pady=5)

        # End Date for Recurrence
        tk.Label(recurring_task_window, text="End Date (YYYY-MM-DD):").pack(pady=5)
        end_date_var = tk.StringVar()
        end_date_entry = tk.Entry(recurring_task_window, textvariable=end_date_var)
        end_date_entry.pack(pady=5)

        # Task Status Selection
        tk.Label(recurring_task_window, text="Task Status:").pack(pady=10)

        status_var = tk.StringVar(value="Unfinished")

        status_frame = tk.Frame(recurring_task_window)
        status_frame.pack(pady=5)
        tk.Radiobutton(status_frame, text="Unfinished", variable=status_var, value="Unfinished").pack(anchor=tk.W)
        tk.Radiobutton(status_frame, text="Work in Progress", variable=status_var, value="Work in Progress").pack(anchor=tk.W)
        tk.Radiobutton(status_frame, text="Completed", variable=status_var, value="Completed").pack(anchor=tk.W)

        # Confirm Button
        def confirm_add_recurring_tasks():
            task_name = task_name_var.get()
            category = category_var.get()
            status = status_var.get()
            recurrence = recurrence_var.get()
            end_date_str = end_date_var.get()

            # Validate input
            if not task_name or not category:
                messagebox.showerror("Error", "Task name and category cannot be empty!")
                return

            try:
                # Convert end_date string to date object
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Error", "Invalid end date format! Use YYYY-MM-DD.")
                return

            hour = hour_var.get()
            minute = minute_var.get()
            am_pm = am_pm_var.get()

            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0

            due_time = f"{hour % 12 or 12}:{minute:02d} {am_pm}"

            # Convert start_date to date object (assuming self.date_key is a string)
            try:
                start_date = datetime.strptime(self.date_key, "%Y-%m-%d").date()  # Adjust this format if needed
            except ValueError:
                messagebox.showerror("Error", "Invalid start date format!")
                return

            # Calculate recurring dates
            recurrence_dates = self.get_recurrence_dates(start_date, end_date, recurrence)

            # Add tasks for all recurring dates
            for date in recurrence_dates:
                new_task = {
                    "name": task_name,
                    "category": category,
                    "status": status,
                    "due_time": due_time
                }

                # Ensure the date exists in the task dictionary
                date_key = date.strftime("%Y-%m-%d")
                if date_key not in self.calendar_app.tasks:
                    self.calendar_app.tasks[date_key] = []
                self.calendar_app.tasks[date_key].append(new_task)

            # Call the save function to persist changes
            self.calendar_app.save_tasks()
            self.load_tasks()
            self.calendar_app.show_calendar(self.calendar_app.current_year, self.calendar_app.current_month)
            recurring_task_window.destroy()

        confirm_button=tk.Button(recurring_task_window, text="Add Task", command=confirm_add_recurring_tasks)
        confirm_button.pack(pady=20)

    def get_recurrence_dates(self, start_date, end_date, recurrence):
        """Generate a list of dates for the recurring task based on the recurrence pattern."""
        dates = []
        current_date = start_date

        while current_date <= end_date:
            dates.append(current_date)

            if recurrence == "Daily":
                current_date += timedelta(days=1)
            elif recurrence == "Every Other Day":
                current_date += timedelta(days=2)
            elif recurrence == "Weekly":
                current_date += timedelta(weeks=1)
            elif recurrence == "Every Other Week":
                current_date += timedelta(weeks=2)
            elif recurrence == "Monthly":
                # Handle month changes
                next_month = current_date.month % 12 + 1
                year_adjust = current_date.year + (1 if next_month == 1 else 0)
                current_date = current_date.replace(year=year_adjust, month=next_month)

        return dates

    def edit_task(self):
        selected_index = self.task_list.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return

        task_index = selected_index[0]
        task = self.calendar_app.tasks[self.date_key][task_index]

        edit_task_window = tk.Toplevel(self.top)
        edit_task_window.title("Edit Task")
        edit_task_window.geometry("500x500")  # Increased size for better visibility

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

        # Move Task Button
        def move_task():
            self.open_calendar_for_move(task, task_index)

        move_button = tk.Button(edit_task_window, text="Move Task", command=move_task)
        move_button.pack(pady=10)

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
            self.calendar_app.show_calendar(self.calendar_app.current_year, self.calendar_app.current_month)
            self.close_all_windows_except_main()  # Close all windows except the main calendar window

        confirm_button = tk.Button(edit_task_window, text="Save Changes", command=confirm_edit_task)
        confirm_button.pack(pady=20)

    def open_calendar_for_move(self, task, task_index):
        move_window = tk.Toplevel(self.top)
        move_window.title("Select Date to Move Task")
        move_window.geometry("900x600")

        calendar_frame = tk.Frame(move_window)
        calendar_frame.pack(expand=True, fill=tk.BOTH)

        # Show calendar for the current month
        from task_calendar import TaskCalendar
        calendar_app = TaskCalendar(move_window)
        calendar_app.show_calendar(self.calendar_app.current_year, self.calendar_app.current_month)

        def on_date_select(year, month, day):
            destination_date_key = f"{year}-{month:02d}-{day:02d}"
            if messagebox.askyesno("Confirm Move", f"Are you sure you want to move this task to {day}/{month}/{year}?"):
                if destination_date_key not in self.calendar_app.tasks:
                    self.calendar_app.tasks[destination_date_key] = []
                self.calendar_app.tasks[destination_date_key].append(task)
                del self.calendar_app.tasks[self.date_key][task_index]
                self.calendar_app.save_tasks()
                self.load_tasks()
                self.calendar_app.show_calendar(self.calendar_app.current_year, self.calendar_app.current_month)
                move_window.destroy()  # Ensure move window is closed
                self.close_all_windows_except_main()  # Ensure all other windows are closed

        # Add functionality to the calendar buttons to move the task
        calendar_app.open_task_window = lambda y, m, d: on_date_select(y, m, d)

    def close_all_windows_except_main(self):
        # Close all Toplevel windows except the main task calendar window
        for window in self.top.master.winfo_children():
            if isinstance(window, tk.Toplevel) and window != self.top:
                window.destroy()
        self.top.destroy()  # Ensure the current task window is closed

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
            self.calendar_app.show_calendar(self.calendar_app.current_year, self.calendar_app.current_month)
