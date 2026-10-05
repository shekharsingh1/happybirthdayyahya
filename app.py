import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os

DB_NAME = "employees.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            employee_id TEXT NOT NULL UNIQUE,
            department TEXT,
            job_title TEXT,
            start_date TEXT,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

class EmployeeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Registration System")
        self.geometry("900x600")

        # Initialize Database
        init_db()

        # Create Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab 1: Register
        self.tab_register = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_register, text="Register Employee")
        self.setup_register_tab()

        # Tab 2: View List
        self.tab_view = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_view, text="View Employees")
        self.setup_view_tab()

    def setup_register_tab(self):
        frame = ttk.Frame(self.tab_register, padding="20")
        frame.pack(expand=True, fill='both')

        # Variables
        self.full_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.employee_id_var = tk.StringVar()
        self.department_var = tk.StringVar()
        self.job_title_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.password_var = tk.StringVar()

        fields = [
            ("Full Name:", self.full_name_var, False),
            ("Email:", self.email_var, False),
            ("Employee ID:", self.employee_id_var, False),
            ("Department:", self.department_var, False),
            ("Job Title:", self.job_title_var, False),
            ("Start Date (YYYY-MM-DD):", self.start_date_var, False),
            ("Password:", self.password_var, True)
        ]

        for i, (label_text, variable, is_password) in enumerate(fields):
            ttk.Label(frame, text=label_text).grid(row=i, column=0, sticky='w', pady=5, padx=5)
            entry = ttk.Entry(frame, textvariable=variable, width=40)
            if is_password:
                entry.config(show="*")
            entry.grid(row=i, column=1, sticky='w', pady=5, padx=5)

        ttk.Button(frame, text="Register", command=self.register_employee).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def register_employee(self):
        full_name = self.full_name_var.get().strip()
        email = self.email_var.get().strip()
        employee_id = self.employee_id_var.get().strip()
        department = self.department_var.get().strip()
        job_title = self.job_title_var.get().strip()
        start_date = self.start_date_var.get().strip()
        password = self.password_var.get().strip()

        if not all([full_name, email, employee_id, password]):
            messagebox.showerror("Error", "Full Name, Email, Employee ID, and Password are required.")
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO employees (full_name, email, employee_id, department, job_title, start_date, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (full_name, email, employee_id, department, job_title, start_date, password))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Employee {full_name} registered successfully!")
            self.clear_form()
            self.load_employees()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Employee ID {employee_id} already exists.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_form(self):
        self.full_name_var.set("")
        self.email_var.set("")
        self.employee_id_var.set("")
        self.department_var.set("")
        self.job_title_var.set("")
        self.start_date_var.set("")
        self.password_var.set("")

    def setup_view_tab(self):
        frame = ttk.Frame(self.tab_view, padding="10")
        frame.pack(expand=True, fill='both')

        columns = ("id", "full_name", "email", "employee_id", "department", "job_title", "start_date")
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("full_name", text="Full Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("employee_id", text="Employee ID")
        self.tree.heading("department", text="Department")
        self.tree.heading("job_title", text="Job Title")
        self.tree.heading("start_date", text="Start Date")

        # Define column widths
        self.tree.column("id", width=30)
        self.tree.column("full_name", width=150)
        self.tree.column("email", width=150)
        self.tree.column("employee_id", width=100)
        self.tree.column("department", width=120)
        self.tree.column("job_title", width=120)
        self.tree.column("start_date", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(expand=True, fill='both')

        # Refresh button
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        ttk.Button(btn_frame, text="Refresh List", command=self.load_employees).pack(side=tk.RIGHT)

        # Initial load
        self.load_employees()

    def load_employees(self):
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            # Deliberately NOT selecting the password column
            cursor.execute('''
                SELECT id, full_name, email, employee_id, department, job_title, start_date
                FROM employees
            ''')
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            conn.close()
        except Exception as e:
            if not os.environ.get('DISPLAY') is None:
                messagebox.showerror("Error", f"Failed to load employees: {str(e)}")
            else:
                print(f"Error loading employees: {str(e)}")

if __name__ == "__main__":
    if os.environ.get('DISPLAY') is None:
        print("Skipping Tkinter window initialization for test environment (no display).")
        init_db()
        # Mock load to test query
        app_mock = type("MockApp", (object,), {"tree": type("MockTree", (object,), {"get_children": lambda s: [], "insert": lambda s, a, b, values: print(f"Inserted: {values}")})()})()

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, full_name, email, employee_id, department, job_title, start_date
                FROM employees
            ''')
            rows = cursor.fetchall()
            for row in rows:
                app_mock.tree.insert("", "end", values=row)
            conn.close()
            print("Employee query successful.")
        except Exception as e:
            print(f"Error: {e}")

    else:
        app = EmployeeApp()
        app.mainloop()
