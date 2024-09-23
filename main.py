import tkinter as tk
from task_calendar import TaskCalendar
import time
import threading
from plyer import notification
from datetime import datetime, timedelta
import json


def initial_load_tasks():
    """Load tasks from tasks.json file."""
    tasks = []
    try:
        with open('tasks.json', 'r') as file:
            data = json.load(file)
            print("Loaded data:", data)  # Debugging output

            # Flatten the tasks from the JSON structure
            for date, task_list in data.items():
                for task in task_list:
                    due_date_str = f"{date} {task['due_time']}"
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d %I:%M %p")  # Convert to datetime
                    task['due_date'] = due_date  # Add due_date to task
                    tasks.append(task)  # Add the task to the main list

            return tasks

    except FileNotFoundError:
        print("tasks.json not found. Returning empty task list.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON. Returning empty task list.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}. Returning empty task list.")
        return []


def send_notification(task_name, time_remaining):
    notification.notify(
        title=f"Task Reminder: {task_name}",
        message=f"{task_name} is due in {time_remaining} hours!",
        timeout=10
    )


def check_task_deadlines():
    last_notification_time = {}  # Dictionary to track last notification time for each task

    while True:
        tasks = initial_load_tasks()  # Load tasks every iteration
        current_time = datetime.now()

        for task in tasks:
            print("Current task being processed:", task)  # Debugging output

            if isinstance(task, dict):
                task_name = task['name']
                due_date = task['due_date']  # This should be a datetime object
                time_to_due = due_date - current_time

                # Determine the time interval for notifications
                if time_to_due <= timedelta(hours=1) and time_to_due > timedelta(hours=0):
                    interval = 1
                elif time_to_due <= timedelta(hours=6) and time_to_due > timedelta(hours=1):
                    interval = 6
                elif time_to_due <= timedelta(hours=12) and time_to_due > timedelta(hours=6):
                    interval = 12
                elif time_to_due <= timedelta(hours=24) and time_to_due > timedelta(hours=12):
                    interval = 24
                elif time_to_due <= timedelta(hours=48) and time_to_due > timedelta(hours=24):
                    interval = 48
                else:
                    continue  # Skip if no notification should be sent

                # Check if notification has already been sent for this interval
                if (task_name not in last_notification_time) or (
                        current_time - last_notification_time[task_name] >= timedelta(hours=interval)):
                    send_notification(task_name, interval)
                    last_notification_time[task_name] = current_time  # Update last notification time
            else:
                print(f"Unexpected task format: {task}")  # Debugging output

        time.sleep(30)  # Check every 30 seconds


def start_notification_service():
    notification_thread = threading.Thread(target=check_task_deadlines)
    notification_thread.daemon = True
    notification_thread.start()


def main():
    start_notification_service()  # Start the notification service

    # Initialize the Tkinter app
    root = tk.Tk()
    app = TaskCalendar(root)
    root.mainloop()


if __name__ == "__main__":
    main()
