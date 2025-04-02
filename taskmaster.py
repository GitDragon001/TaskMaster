import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

TASKS_FILE = 'tasks.json'

class TaskMasterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TaskMaster Advanced")
        self.geometry("700x400")
        self.tasks = []
        self.load_tasks()
        self.create_widgets()

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as file:
                    self.tasks = json.load(file)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading tasks: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        with open(TASKS_FILE, 'w') as file:
            json.dump(self.tasks, file, indent=4)

    def create_widgets(self):
        # Frame for action buttons
        button_frame = tk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)

        tk.Button(button_frame, text="Add Task", command=self.add_task).pack(side='left', padx=5)
        tk.Button(button_frame, text="Edit Task", command=self.edit_task).pack(side='left', padx=5)
        tk.Button(button_frame, text="Toggle Complete", command=self.toggle_complete).pack(side='left', padx=5)
        tk.Button(button_frame, text="Delete Task", command=self.delete_task).pack(side='left', padx=5)
        tk.Button(button_frame, text="Clear Completed", command=self.clear_completed).pack(side='left', padx=5)

        # Treeview to display tasks with columns for task details
        columns = ("task", "due_date", "priority", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("task", text="Task")
        self.tree.heading("due_date", text="Due Date")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("status", text="Status")
        self.tree.column("task", width=300)
        self.tree.column("due_date", width=100)
        self.tree.column("priority", width=80)
        self.tree.column("status", width=80)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)

        self.populate_tree()

    def populate_tree(self):
        # Clear existing entries in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insert each task from our list
        for idx, task in enumerate(self.tasks):
            status = "Done" if task.get("completed", False) else "Pending"
            self.tree.insert("", "end", iid=idx, values=(task.get("task"), task.get("due_date"), task.get("priority"), status))

    def add_task(self):
        TaskDialog(self, "Add Task", self.add_task_callback)

    def add_task_callback(self, task_data):
        self.tasks.append(task_data)
        self.save_tasks()
        self.populate_tree()

    def edit_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to edit.")
            return
        idx = int(selected[0])
        task = self.tasks[idx]
        TaskDialog(self, "Edit Task", self.edit_task_callback, task, idx)

    def edit_task_callback(self, task_data, idx):
        self.tasks[idx] = task_data
        self.save_tasks()
        self.populate_tree()

    def toggle_complete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to toggle.")
            return
        idx = int(selected[0])
        self.tasks[idx]["completed"] = not self.tasks[idx].get("completed", False)
        self.save_tasks()
        self.populate_tree()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        idx = int(selected[0])
        del self.tasks[idx]
        self.save_tasks()
        self.populate_tree()

    def clear_completed(self):
        self.tasks = [task for task in self.tasks if not task.get("completed", False)]
        self.save_tasks()
        self.populate_tree()

class TaskDialog(tk.Toplevel):
    def __init__(self, parent, title, callback, task_data=None, idx=None):
        super().__init__(parent)
        self.title(title)
        self.callback = callback
        self.idx = idx
        self.geometry("400x250")
        self.resizable(False, False)
        self.create_widgets(task_data)
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def create_widgets(self, task_data):
        # Task description
        tk.Label(self, text="Task Description:").pack(pady=5)
        self.task_entry = tk.Entry(self, width=50)
        self.task_entry.pack(pady=5)

        # Due date entry
        tk.Label(self, text="Due Date (YYYY-MM-DD):").pack(pady=5)
        self.due_entry = tk.Entry(self, width=20)
        self.due_entry.pack(pady=5)

        # Priority selection
        tk.Label(self, text="Priority:").pack(pady=5)
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(self, textvariable=self.priority_var, 
                                           values=["High", "Medium", "Low"], state="readonly")
        self.priority_combo.pack(pady=5)
        self.priority_combo.current(1)  # Default to Medium

        # If editing, fill in current task details
        if task_data:
            self.task_entry.insert(0, task_data.get("task", ""))
            self.due_entry.insert(0, task_data.get("due_date", ""))
            self.priority_combo.set(task_data.get("priority", "Medium"))

        # Save button
        tk.Button(self, text="Save", command=self.on_save).pack(pady=10)

    def on_save(self):
        task_desc = self.task_entry.get().strip()
        due_date = self.due_entry.get().strip()
        priority = self.priority_var.get()

        if not task_desc:
            messagebox.showwarning("Warning", "Task description cannot be empty.")
            return

        # Validate due date if provided
        if due_date:
            try:
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Warning", "Due date must be in YYYY-MM-DD format.")
                return

        task_data = {
            "task": task_desc,
            "due_date": due_date,
            "priority": priority,
            "completed": False
        }
        if self.idx is not None:
            self.callback(task_data, self.idx)
        else:
            self.callback(task_data)
        self.destroy()

if __name__ == "__main__":
    app = TaskMasterApp()
    app.mainloop()
