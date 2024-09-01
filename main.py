import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import pandas as pd

def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    date_added TEXT NOT NULL,
                    date_completed TEXT)''')
    conn.commit()
    conn.close()

init_db()


class todo:
    def __init__(self, root):
        self.root = root
        self.root.title('taskmaster')
        self.root.geometry("700x500")
        self.root.configure(bg='#333333')

        self.task_var = tk.StringVar()
        self.date_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background='#333333')
        style.configure('TLabel', background='#333333', foreground='white')
        style.configure('TButton', background='#666666', foreground='white')
        style.configure('TEntry', fieldbackground='#555555', foreground='white')
        style.configure('Treeview', background='#444444', fieldbackground ='#444444', foreground='white', bordercolor='#333333')
        style.configure('Treeview.Heading', background='#555555', foreground='white')

        frame = ttk.Frame(self.root, padding="10 10 10 10")
        frame.pack(fill=tk.BOTH, expand=True)


        ttk.Label(frame, text='new task:').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.task_entry = ttk.Entry(frame, textvariable=self.task_var, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(frame, text="due date:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.task_entry = ttk.Entry(frame, textvariable=self.task_var, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(frame, text="due date:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.date_entry = DateEntry(frame, textvariable=self.date_var, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Button(frame, text="add task", command=self.add_task).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame, text="completed tasks", command=self.show_completed_tasks).grid(row=1, column=2, padx=5, pady=5)

        
        self.tree = ttk.Treeview(frame, columns=('ID', 'Task', 'Due Date', 'Status'), show='headings')
        self.tree.heading('ID', text='iD')
        self.tree.heading('Task', text='task')
        self.tree.heading('Due Date', text='due date')
        self.tree.heading('Status', text='status')
        self.tree.column('ID', width=30)
        self.tree.column('Task', width=250)
        self.tree.column('Due Date', width=100)
        self.tree.column('Status', width=100)
        self.tree.grid(row=2, column=0, columnspan=3, pady=10, padx=5, sticky=tk.NSEW)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        
        self.mark_done_button = ttk.Button(frame, text="Mark as Done", command=self.mark_task_done, state=tk.DISABLED)
        self.mark_done_button.grid(row=3, column=0, padx=5, pady=5)
        
        self.delete_button = ttk.Button(frame, text="Delete Task", command=self.delete_task, state=tk.DISABLED)
        self.delete_button.grid(row=3, column=1, padx=5, pady=5)

        self.load_tasks()

    def load_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT id, task, date_added, status FROM tasks WHERE status = 'pending'")
        for row in c.fetchall():
            self.tree.insert('', tk.END, values=row)
        conn.close()

    def add_task(self):
        task = self.task_var.get()
        due_date = self.date_var.get()
        if task:
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("INSERT INTO tasks (task, status, date_added) VALUES (?, 'pending', ?)",
                      (task, due_date))
            conn.commit()
            conn.close()
            self.task_var.set("")
            self.date_var.set("")
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def delete_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)['values'][0]
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "You must select a task to delete.")

    def mark_task_done(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)['values'][0]
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("UPDATE tasks SET status = 'done', date_completed = ? WHERE id = ?",
                      (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id))
            conn.commit()
            conn.close()
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "You must select a task to mark as done.")

    def show_completed_tasks(self):
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task, date_completed FROM tasks WHERE status = 'done'")
        completed_tasks = c.fetchall()
        conn.close()

        completed_window = tk.Toplevel(self.root)
        completed_window.title("Completed Tasks")
        completed_window.geometry("500x300")
        completed_window.configure(bg="#333333")

        tree = ttk.Treeview(completed_window, columns=('Task', 'Completion Date'), show='headings')
        tree.heading('Task', text='Task')
        tree.heading('Completion Date', text='Completion Date')
        tree.column('Task', width=250)
        tree.column('Completion Date', width=150)
        tree.pack(fill=tk.BOTH, expand=True)

        for task in completed_tasks:
            tree.insert('', tk.END, values=task)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.mark_done_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.mark_done_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)



if __name__ == "__main__":
    root= tk.Tk()
    app = todo(root)
    root.mainloop()