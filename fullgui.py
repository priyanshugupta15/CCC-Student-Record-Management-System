import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Files (same as your C program)
STUD_FILE = "students.txt"
CRE_FILE = "credentials.txt"
TEMP_FILE = "temp.txt"

# Ensure files exist and default credentials exist
DEFAULT_CRE = [("admin", "admin", "admin"), ("student", "student", "student")]

def ensure_credentials():
    if not os.path.exists(CRE_FILE):
        with open(CRE_FILE, "w", encoding="utf-8") as f:
            for u, p, r in DEFAULT_CRE:
                f.write(f"{u} {p} {r}\n")

def read_credentials():
    ensure_credentials()
    creds = []
    with open(CRE_FILE, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln: continue
            parts = ln.split()
            if len(parts) >= 3:
                # allow passwords or roles with spaces? C code used 3 tokens; keep same
                u, p, r = parts[0], parts[1], parts[2]
                creds.append((u, p, r))
    return creds

def write_credentials(creds):
    with open(CRE_FILE, "w", encoding="utf-8") as f:
        for u, p, r in creds:
            f.write(f"{u} {p} {r}\n")

def username_exists(username):
    for u, p, r in read_credentials():
        if u == username:
            return True
    return False

def add_user_to_file(username, password, role):
    if username_exists(username):
        return False
    creds = read_credentials()
    creds.append((username, password, role))
    write_credentials(creds)
    return True

def remove_user_from_file(username):
    creds = read_credentials()
    new = [c for c in creds if c[0] != username]
    if len(new) == len(creds):
        return False
    write_credentials(new)
    return True

def update_password_in_file(username, newpass):
    creds = read_credentials()
    found = False
    for i, (u, p, r) in enumerate(creds):
        if u == username:
            creds[i] = (u, newpass, r)
            found = True
            break
    if not found: return False
    write_credentials(creds)
    return True

# Student file helpers
def read_students():
    students = []
    if not os.path.exists(STUD_FILE):
        return students
    with open(STUD_FILE, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln: continue
            parts = ln.split("|")
            if len(parts) == 3:
                try:
                    roll = int(parts[0])
                    name = parts[1]
                    mark = float(parts[2])
                    students.append((roll, name, mark))
                except:
                    continue
    return students

def write_students(students):
    with open(STUD_FILE, "w", encoding="utf-8") as f:
        for roll, name, mark in students:
            f.write(f"{roll}|{name}|{mark:.2f}\n")

def add_student(roll, name, mark):
    students = read_students()
    for r, _, _ in students:
        if r == roll:
            return False
    students.append((roll, name, mark))
    write_students(students)
    return True

def update_student_record(roll, name, mark):
    students = read_students()
    found = False
    for i, (r, _, _) in enumerate(students):
        if r == roll:
            students[i] = (roll, name, mark)
            found = True
            break
    if not found: return False
    write_students(students)
    return True

def delete_student_record(roll):
    students = read_students()
    new = [s for s in students if s[0] != roll]
    if len(new) == len(students):
        return False
    write_students(new)
    return True

def find_student(roll):
    for r, n, m in read_students():
        if r == roll:
            return (r, n, m)
    return None

# GUI Application
class App:
    def __init__(self, root):
        self.root = root
        root.title("Student Management System")
        root.geometry("720x480")
        self.current_user = None
        self.current_role = None

        self.login_frame = None
        self.admin_frame = None
        self.student_frame = None

        self.build_login()

    def clear_frames(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ----------------- Login -----------------
    def build_login(self):
        self.clear_frames()
        ensure_credentials()

        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="Login", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,10))

        tk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", padx=(0,5))
        self.ent_user = tk.Entry(frame)
        self.ent_user.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", padx=(0,5))
        self.ent_pass = tk.Entry(frame, show="*")
        self.ent_pass.grid(row=2, column=1, pady=5)

        btn_login = tk.Button(frame, text="Login", width=12, command=self.try_login)
        btn_login.grid(row=3, column=0, pady=10)

        btn_quit = tk.Button(frame, text="Quit", width=12, command=self.root.quit)
        btn_quit.grid(row=3, column=1, pady=10)

        # Hint: show default creds
        tk.Label(frame, text="(default admin/admin/admin)").grid(row=4, column=0, columnspan=2, pady=(10,0))

    def try_login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Login", "Enter username and password")
            return
        for fu, fpw, fr in read_credentials():
            if u == fu and p == fpw:
                self.current_user = fu
                self.current_role = fr.lower()
                if self.current_role == "admin":
                    self.build_admin()
                elif self.current_role == "student":
                    self.build_student()
                else:
                    messagebox.showerror("Login", "Access denied: only admin or student allowed")
                    self.current_user = None
                return
        messagebox.showerror("Login", "Invalid username or password")

    # ----------------- Admin -----------------
    def build_admin(self):
        self.clear_frames()
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack(fill="x")
        tk.Label(top, text=f"Admin: {self.current_user}", font=("Arial", 14)).pack(side="left")
        tk.Button(top, text="Logout", command=self.logout).pack(side="right", padx=5)
        tk.Button(top, text="Change Password", command=self.change_password).pack(side="right", padx=5)

        # Left menu
        left = tk.Frame(self.root, width=200, padx=10, pady=10)
        left.pack(side="left", fill="y")

        btn_add = tk.Button(left, text="Add Student", width=20, command=self.dialog_add_student)
        btn_add.pack(pady=5)
        btn_view = tk.Button(left, text="View Students", width=20, command=self.build_students_table)
        btn_view.pack(pady=5)
        btn_search = tk.Button(left, text="Search Student", width=20, command=self.dialog_search_student)
        btn_search.pack(pady=5)
        btn_update = tk.Button(left, text="Update Student", width=20, command=self.dialog_update_student)
        btn_update.pack(pady=5)
        btn_delete = tk.Button(left, text="Delete Student", width=20, command=self.dialog_delete_student)
        btn_delete.pack(pady=5)

        # User management
        tk.Label(left, text="User Management", font=("Arial", 10, "bold")).pack(pady=(20,5))
        tk.Button(left, text="Create User", width=20, command=self.dialog_create_user).pack(pady=3)
        tk.Button(left, text="Delete User", width=20, command=self.dialog_delete_user).pack(pady=3)

        # Right area (table)
        self.table_frame = tk.Frame(self.root, padx=10, pady=10)
        self.table_frame.pack(side="right", fill="both", expand=True)
        self.build_students_table()

    # ----------------- Student -----------------
    def build_student(self):
        self.clear_frames()
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack(fill="x")
        tk.Label(top, text=f"Student: {self.current_user}", font=("Arial", 14)).pack(side="left")
        tk.Button(top, text="Logout", command=self.logout).pack(side="right", padx=5)
        tk.Button(top, text="Change Password", command=self.change_password).pack(side="right", padx=5)

        left = tk.Frame(self.root, width=200, padx=10, pady=10)
        left.pack(side="left", fill="y")

        tk.Button(left, text="View Students", width=20, command=self.build_students_table).pack(pady=5)
        tk.Button(left, text="Search Student", width=20, command=self.dialog_search_student).pack(pady=5)

        self.table_frame = tk.Frame(self.root, padx=10, pady=10)
        self.table_frame.pack(side="right", fill="both", expand=True)
        self.build_students_table()

    # ----------------- Shared UI pieces -----------------
    def build_students_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        cols = ("roll", "name", "mark")
        tree = ttk.Treeview(self.table_frame, columns=cols, show="headings")
        tree.heading("roll", text="Roll")
        tree.heading("name", text="Name")
        tree.heading("mark", text="Mark")
        tree.column("roll", width=80, anchor="center")
        tree.column("name", width=300)
        tree.column("mark", width=80, anchor="center")

        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for r, n, m in read_students():
            tree.insert("", "end", values=(r, n, f"{m:.2f}"))

    # ----------------- Dialogs / Actions -----------------
    def dialog_add_student(self):
        d = tk.Toplevel(self.root)
        d.title("Add Student")
        d.geometry("320x200")
        tk.Label(d, text="Roll:").pack(pady=(10,0))
        ent_roll = tk.Entry(d)
        ent_roll.pack()
        tk.Label(d, text="Name:").pack(pady=(10,0))
        ent_name = tk.Entry(d)
        ent_name.pack()
        tk.Label(d, text="Mark:").pack(pady=(10,0))
        ent_mark = tk.Entry(d)
        ent_mark.pack()

        def on_add():
            try:
                roll = int(ent_roll.get().strip())
                name = ent_name.get().strip()
                mark = float(ent_mark.get().strip())
            except:
                messagebox.showerror("Add Student", "Enter valid roll (int) and mark (number).")
                return
            if not name:
                messagebox.showerror("Add Student", "Enter name.")
                return
            if add_student(roll, name, mark):
                messagebox.showinfo("Add Student", "Student added.")
                d.destroy()
                self.build_students_table()
            else:
                messagebox.showerror("Add Student", "Roll already exists.")

        tk.Button(d, text="Add", command=on_add).pack(pady=10)

    def dialog_search_student(self):
        s = simpledialog.askstring("Search Student", "Enter roll to search:")
        if s is None: return
        try:
            roll = int(s.strip())
        except:
            messagebox.showerror("Search", "Enter valid integer roll.")
            return
        res = find_student(roll)
        if res:
            r, n, m = res
            messagebox.showinfo("Found", f"Found: {r} | {n} | {m:.2f}")
        else:
            messagebox.showinfo("Not found", "Student not found.")

    def dialog_update_student(self):
        s = simpledialog.askstring("Update Student", "Enter roll to update:")
        if s is None: return
        try:
            roll = int(s.strip())
        except:
            messagebox.showerror("Update", "Enter valid integer roll.")
            return
        existing = find_student(roll)
        if not existing:
            messagebox.showinfo("Update", "Roll not found.")
            return
        r, n, m = existing
        d = tk.Toplevel(self.root)
        d.title("Update Student")
        d.geometry("320x200")
        tk.Label(d, text=f"Updating roll {r}").pack(pady=(8,0))
        tk.Label(d, text="Name:").pack()
        ent_name = tk.Entry(d)
        ent_name.insert(0, n)
        ent_name.pack()
        tk.Label(d, text="Mark:").pack()
        ent_mark = tk.Entry(d)
        ent_mark.insert(0, f"{m:.2f}")
        ent_mark.pack()

        def on_update():
            try:
                name = ent_name.get().strip()
                mark = float(ent_mark.get().strip())
            except:
                messagebox.showerror("Update", "Enter valid mark.")
                return
            if not name:
                messagebox.showerror("Update", "Enter name.")
                return
            if update_student_record(r, name, mark):
                messagebox.showinfo("Update", "Record updated.")
                d.destroy()
                self.build_students_table()
            else:
                messagebox.showerror("Update", "Failed to update.")

        tk.Button(d, text="Update", command=on_update).pack(pady=10)

    def dialog_delete_student(self):
        s = simpledialog.askstring("Delete Student", "Enter roll to delete:")
        if s is None: return
        try:
            roll = int(s.strip())
        except:
            messagebox.showerror("Delete", "Enter valid integer roll.")
            return
        if not find_student(roll):
            messagebox.showinfo("Delete", "Roll not found.")
            return
        if messagebox.askyesno("Confirm", f"Delete roll {roll}?"):
            if delete_student_record(roll):
                messagebox.showinfo("Delete", "Student deleted.")
                self.build_students_table()
            else:
                messagebox.showerror("Delete", "Failed to delete.")

    # User management dialogs
    def dialog_create_user(self):
        d = tk.Toplevel(self.root)
        d.title("Create User")
        d.geometry("320x220")
        tk.Label(d, text="Username:").pack(pady=(8,0))
        ent_u = tk.Entry(d); ent_u.pack()
        tk.Label(d, text="Password:").pack()
        ent_p = tk.Entry(d, show="*"); ent_p.pack()
        tk.Label(d, text="Role (admin/student):").pack()
        ent_r = tk.Entry(d); ent_r.pack()

        def on_create():
            u = ent_u.get().strip()
            p = ent_p.get().strip()
            r = ent_r.get().strip().lower()
            if not u or not p or not r:
                messagebox.showerror("Create User", "Fill all fields.")
                return
            if r not in ("admin", "student"):
                messagebox.showerror("Create User", "Role must be 'admin' or 'student'.")
                return
            if add_user_to_file(u, p, r):
                messagebox.showinfo("Create User", f"User '{u}' created.")
                d.destroy()
            else:
                messagebox.showerror("Create User", "User already exists.")

        tk.Button(d, text="Create", command=on_create).pack(pady=10)

    def dialog_delete_user(self):
        s = simpledialog.askstring("Delete User", "Enter username to delete:")
        if s is None: return
        uname = s.strip()
        if uname == self.current_user:
            messagebox.showwarning("Delete User", "Cannot delete the account you are logged in with.")
            return
        if not username_exists(uname):
            messagebox.showinfo("Delete User", "User does not exist.")
            return
        if messagebox.askyesno("Confirm", f"Delete user '{uname}'?"):
            if remove_user_from_file(uname):
                messagebox.showinfo("Delete User", "User removed.")
            else:
                messagebox.showerror("Delete User", "Failed to remove user.")

    def change_password(self):
        s = simpledialog.askstring("Change Password", "Enter new password:", show="*")
        if s is None: return
        newpass = s.strip()
        if not newpass:
            messagebox.showerror("Change Password", "Invalid password.")
            return
        if update_password_in_file(self.current_user, newpass):
            messagebox.showinfo("Password", "Password updated. Please login again.")
            self.current_user = None
            self.current_role = None
            self.build_login()
        else:
            messagebox.showerror("Password", "Failed to update password.")

    def logout(self):
        self.current_user = None
        self.current_role = None
        self.build_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
