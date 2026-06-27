import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import hashlib
import time
import re
from datetime import datetime

# ===== Vigenere Cipher (demo only) =====
CHAR_SET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !@#$%^&*()-_=+[]{}|;:',.<>/?`~\\\""
VIGENERE_KEY = "SecureKey123"

def vigenere_encrypt(text, key):
    result = ""
    for i, ch in enumerate(text):
        if ch not in CHAR_SET:
            result += ch
            continue
        ti = CHAR_SET.index(ch)
        ki = CHAR_SET.index(key[i % len(key)])
        result += CHAR_SET[(ti + ki) % len(CHAR_SET)]
    return result

def vigenere_decrypt(text, key):
    result = ""
    for i, ch in enumerate(text):
        if ch not in CHAR_SET:
            result += ch
            continue
        ti = CHAR_SET.index(ch)
        ki = CHAR_SET.index(key[i % len(key)])
        result += CHAR_SET[(ti - ki) % len(CHAR_SET)]
    return result

# ===== File helpers =====
def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def log(action):
    with open("activity.log", "a") as f:
        f.write(f"{datetime.now()} - {action}\n")

# ===== Lock & attempts =====
lock_time = {}   # username -> unlock_timestamp
attempts = {}    # username -> remaining attempts
MAX_ATTEMPTS = 3
LOCK_SECONDS = 60

def lock_user(username, seconds=LOCK_SECONDS):
    lock_time[username] = time.time() + seconds
    attempts[username] = MAX_ATTEMPTS

def is_locked(username):
    return username in lock_time and time.time() < lock_time[username]

def remaining_lock_seconds(username):
    if username in lock_time:
        return max(0, int(lock_time[username] - time.time()))
    return 0

def reset_attempts(username):
    attempts[username] = MAX_ATTEMPTS

# ===== Password strength checker =====
def check_strength(password):
    """Return (label, color) for password strength."""
    if not password:
        return ("", "black")
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[^a-zA-Z0-9]", password):
        score += 1

    if score <= 2:
        return ("Weak", "#d9534f")       # muted red
    elif 3 <= score <= 4:
        return ("Medium", "#f0ad4e")     # warm amber
    else:
        return ("Strong", "#5cb85c")     # soft green

# ===== App =====
class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Password Manager System")
        # Default size; attempt to maximize
        self.geometry("1000x700")
        self.resizable(True, True)
        try:
            self.state('zoomed')
        except Exception:
            try:
                self.attributes('-zoomed', True)
            except Exception:
                pass

        # Fullscreen toggle
        self.fullscreen = False
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.exit_fullscreen())

        # Theme colors: elegant, muted contrast
        self.bg = "#1f2933"        # deep slate
        self.panel = "#26323b"     # slightly lighter panel
        self.card = "#2b3a42"      # card background
        self.accent = "#7aa2b8"    # soft teal accent
        self.text = "#e6eef2"      # light text
        self.muted = "#9fb0b6"     # muted text

        self.configure(bg=self.bg)

        # ttk style tweaks
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=self.panel)
        style.configure("Card.TFrame", background=self.card)
        style.configure("TLabel", background=self.panel, foreground=self.text, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.panel, foreground=self.accent, font=("Segoe UI", 26, "bold"))
        style.configure("Header.TLabel", background=self.panel, foreground=self.text, font=("Segoe UI", 26, "bold"))
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("Big.TButton", padding=10, font=("Segoe UI", 11))
        style.configure("Accent.TButton", background=self.accent, foreground=self.bg, font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#6b98a9")])

        style.configure("Treeview", background=self.card, fieldbackground=self.card, foreground=self.text, rowheight=26)
        style.configure("Treeview.Heading", background=self.panel, foreground=self.accent, font=("Segoe UI", 10, "bold"))

        # Tree alternating rows
        self.row_colors = ("#2b3a42", "#24333a")

        self.current_user = None
        self.tree = None

        self.show_main_menu()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self):
        if self.fullscreen:
            self.fullscreen = False
            self.attributes("-fullscreen", False)

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ---- Main menu / splash ----
    def show_main_menu(self):
        self.clear()
        # central container using place center
        container = ttk.Frame(self, padding=20, style="TFrame")
        container.place(relx=0.5, rely=0.5, anchor="center", width=820, height=420)

        # configure grid to center content
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=0)
        container.rowconfigure(2, weight=1)

        title = ttk.Label(container, text="Secure Password Manager System", style="Title.TLabel", anchor="center")
        title.grid(row=0, column=0, pady=(40, 12), sticky="n")

        btn_frame = ttk.Frame(container, style="TFrame")
        btn_frame.grid(row=1, column=0, pady=12)
        # center buttons inside btn_frame
        btn_frame.columnconfigure((0,1,2), weight=1)

        ttk.Button(btn_frame, text="Register",style="Big.TButton", width=25, command=self.register).grid(row=0, column=0, pady=8)
        ttk.Button(btn_frame, text="Login", width=25,style="Big.TButton", command=self.login).grid(row=1, column=0, pady=8)
        ttk.Button(btn_frame, text="Exit", width=25,style="Big.TButton", command=self.destroy).grid(row=2, column=0, pady=8)

        footer_info = ttk.Label(container, text="Data stored locally in users.json and vault.json", style="TLabel")
        footer_info.grid(row=2, column=0, pady=(12, 20), sticky="s")

    # ---- Register ----
    def register(self):
        self.clear()
        frame = ttk.Frame(self, padding=20, style="TFrame")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=760, height=360)

        # center grid columns
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=2)

        ttk.Label(frame, text="Register", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0,30))

        ttk.Label(frame, text="Username:", style="TLabel", font=("Segoe UI", 13,"bold")).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        username_entry = ttk.Entry(frame, width=45, font=("Segoe UI", 12))
        username_entry.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        ttk.Label(frame, text="Password:", style="TLabel", font=("Segoe UI", 13,"bold")).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        password_entry = ttk.Entry(frame, show="*", width=45, font=("Segoe UI", 12))
        password_entry.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        strength_label = ttk.Label(frame, text="", font=("Segoe UI", 10, "bold"))
        strength_label.grid(row=3, column=1, sticky="w", padx=6, pady=(0,8))

        def on_pwd_key(event=None):
            s, color = check_strength(password_entry.get())
            strength_label.config(text=f"Strength: {s}" if s else "", foreground=color)

        password_entry.bind("<KeyRelease>", on_pwd_key)

        def do_register():
            users = load("users.json")
            u = username_entry.get().strip()
            p = password_entry.get()
            if not u or not p:
                messagebox.showerror("Error", "Fields cannot be empty.")
                return
            if u in users:
                messagebox.showerror("Error", "Username exists.")
                return
            users[u] = hashlib.sha256(p.encode()).hexdigest()
            save("users.json", users)
            reset_attempts(u)
            log(f"Registered: {u}")
            messagebox.showinfo("Success", "Registered.")
            self.show_main_menu()

        btnf = ttk.Frame(frame, style="TFrame")
        btnf.grid(row=4, column=0, columnspan=2, pady=12)
        btnf.columnconfigure((0,1), weight=1)
        ttk.Button(btnf, text="Submit",width=18, command=do_register).grid(row=0, column=0, padx=8)
        ttk.Button(btnf, text="Back",width=18, command=self.show_main_menu).grid(row=0, column=1, padx=8)

    # ---- Login ----
    def login(self):
        self.clear()
        frame = ttk.Frame(self, padding=20, style="TFrame")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=760, height=360)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Login", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0,30))
        ttk.Label(frame, text="Username:", style="TLabel", font=("Segoe UI", 13, "bold")).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        username_entry = ttk.Entry(frame, width=45, font=("Segoe UI", 12))
        username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(frame, text="Password:", style="TLabel", font=("Segoe UI", 13, "bold")).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        password_entry = ttk.Entry(frame, show="*", width=45, font=("Segoe UI", 12))
        password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        def do_login():
            users = load("users.json")
            u = username_entry.get().strip()
            p = password_entry.get()
            if not u or not p:
                messagebox.showerror("Error", "Fields cannot be empty.")
                return
            if is_locked(u):
                rem = remaining_lock_seconds(u)
                self.show_lock_countdown(u, rem)
                return
            hashed = hashlib.sha256(p.encode()).hexdigest()
            if u in users and users[u] == hashed:
                self.current_user = u
                reset_attempts(u)
                log(f"Login success: {u}")
                self.show_vault()
            else:
                attempts.setdefault(u, MAX_ATTEMPTS)
                attempts[u] -= 1
                if attempts[u] <= 0:
                    lock_user(u, LOCK_SECONDS)
                    messagebox.showerror("Locked", f"Too many failed attempts. Locked for {LOCK_SECONDS}s.")
                    self.show_lock_countdown(u, LOCK_SECONDS)
                else:
                    messagebox.showerror("Error", f"Login failed. Attempts left: {attempts[u]}")
                log(f"Login failed: {u}")

        btnf = ttk.Frame(frame, style="TFrame")
        btnf.grid(row=3, column=0, columnspan=2, pady=(25, 12))
        btnf.columnconfigure((0,1), weight=1)
        ttk.Button(btnf, text="Login",width=18, command=do_login).grid(row=0, column=0, padx=8)
        ttk.Button(btnf, text="Back",width=18, command=self.show_main_menu).grid(row=0, column=1, padx=8)

    # ---- Lock countdown modal ----
    def show_lock_countdown(self, username, seconds):
        win = tk.Toplevel(self)
        win.title("Account Locked")
        win.resizable(False, False)
        win.grab_set()
        ttk.Label(win, text=f"Account '{username}' locked", font=("Segoe UI", 12, "bold")).pack(padx=12, pady=(12,6))
        prog = ttk.Progressbar(win, length=360, maximum=seconds, mode="determinate")
        prog.pack(padx=12, pady=(6,12))
        lbl = ttk.Label(win, text=f"Remaining: {seconds} seconds")
        lbl.pack(padx=12, pady=(0,12))

        def tick():
            rem = remaining_lock_seconds(username)
            elapsed = seconds - rem
            prog['value'] = elapsed
            lbl.config(text=f"Remaining: {rem} seconds")
            if rem <= 0:
                try:
                    del lock_time[username]
                except:
                    pass
                reset_attempts(username)
                win.destroy()
                return
            win.after(1000, tick)
        tick()

    # ---- Vault screen ----
    def show_vault(self):
        self.clear()

        # top header area centered
        welcome = ttk.Label(
            self,
            text=f"Welcome, {self.current_user}",
            foreground=self.text,
            font=("Segoe UI", 30, "bold"),
            background=self.bg
        )
        welcome.pack(pady=(5, 0),padx=20, anchor="w", fill="x")
  
        # central table container placed in center with padding
        table_outer = ttk.Frame(self, padding=10, style="TFrame")
        table_outer.place(relx=0.5, rely=0.45, anchor="center", relwidth=0.92, relheight=0.66)

        table_frame = ttk.Frame(table_outer, padding=6, style="TFrame")
        table_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.98)

        cols = ("Site", "Username", "Password", "Action")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=6)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew", padx=(6,0))
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.column("Site", width=360, anchor="w")
        self.tree.column("Username", width=240, anchor="center")
        self.tree.column("Password", width=300, anchor="center")
        self.tree.column("Action", width=60, anchor="center")
        for c in cols:
            self.tree.heading(c, text=c)

        # Alternating row colors
        self.tree.tag_configure('oddrow', background=self.row_colors[0])
        self.tree.tag_configure('evenrow', background=self.row_colors[1])

        # Bind clicks
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.refresh_table()

        # Buttons centered below table
        btns = ttk.Frame(self, padding=10, style="TFrame")
        btns.place(relx=0.5, rely=0.85, anchor="center")
        for i in range(8):
            btns.columnconfigure(i, weight=1)

        ttk.Button(btns, text="Add", width=12, command=self.add_password).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(btns, text="Search", width=12, command=self.search_password).grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(btns, text="Update", width=12, command=self.update_password).grid(row=0, column=2, padx=6, pady=6)
        ttk.Button(btns, text="Delete", width=12, command=self.delete_password).grid(row=0, column=3, padx=6, pady=6)
        ttk.Button(btns, text="Refresh", width=12, command=self.refresh_table).grid(row=0, column=4, padx=6, pady=6)
        ttk.Button(btns, text="Logout", width=12, command=self.logout).grid(row=0, column=5, padx=6, pady=6)
        ttk.Button(btns, text="Exit", width=12, command=self.destroy).grid(row=0, column=6, padx=6, pady=6)

    def refresh_table(self):
        if not self.tree:
            return
        for r in self.tree.get_children():
            self.tree.delete(r)
        vault = load("vault.json")
        if self.current_user in vault:
            idx = 0
            for item in vault[self.current_user]:
                dec = vigenere_decrypt(item["password"], VIGENERE_KEY)
                masked = "•" * max(6, len(dec))
                tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
                self.tree.insert("", "end", values=(item["site"], item["username"], masked, "👁"), tags=(tag,))
                idx += 1

    # ---- Tree interactions ----
    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item:
            return
        if col == "#4":
            vals = self.tree.item(item, "values")
            site, uname = vals[0], vals[1]
            self.show_password_modal(site, uname)

    def on_tree_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        vals = self.tree.item(item, "values")
        site, uname = vals[0], vals[1]
        self.show_password_modal(site, uname)

    def show_password_modal(self, site, uname):
        vault = load("vault.json")
        if self.current_user not in vault:
            messagebox.showerror("Error", "No vault data.")
            return
        for entry in vault[self.current_user]:
            if entry["site"] == site and entry["username"] == uname:
                dec = vigenere_decrypt(entry["password"], VIGENERE_KEY)
                win = tk.Toplevel(self)
                win.title(f"{site} — password")
                win.resizable(False, False)
                win.grab_set()
                frm = ttk.Frame(win, padding=12, style="Card.TFrame")
                frm.pack(fill="both", expand=True)
                frm.columnconfigure(0, weight=1)
                frm.columnconfigure(1, weight=2)
                ttk.Label(frm, text=f"Site: {site}", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))
                ttk.Label(frm, text=f"Username: {uname}", font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0,8))
                ttk.Label(frm, text="Password:").grid(row=2, column=0, sticky="e", padx=(0,6))
                pwd_entry = ttk.Entry(frm, width=40)
                pwd_entry.grid(row=2, column=1, sticky="w")
                pwd_entry.insert(0, dec)
                pwd_entry.state(["readonly"])

                strength_label = ttk.Label(frm, text="", font=("Segoe UI", 10, "bold"))
                strength_label.grid(row=3, column=1, sticky="w", pady=(6,0))
                s, color = check_strength(dec)
                strength_label.config(text=f"Strength: {s}" if s else "", foreground=color)

                def copy_to_clipboard():
                    self.clipboard_clear()
                    self.clipboard_append(dec)
                    messagebox.showinfo("Copied", "Password copied to clipboard.")
                btns = ttk.Frame(frm)
                btns.grid(row=4, column=0, columnspan=2, pady=(10,0))
                ttk.Button(btns, text="Copy", command=copy_to_clipboard).grid(row=0, column=0, padx=6)
                ttk.Button(btns, text="Close", command=win.destroy).grid(row=0, column=1, padx=6)
                return
        messagebox.showerror("Error", "Entry not found.")

    # ---- Add ----
    def add_password(self):
        vault = load("vault.json")
        win = tk.Toplevel(self)
        win.title("Add Password")
        win.resizable(False, False)
        win.grab_set()
        frm = ttk.Frame(win, padding=12, style="Card.TFrame")
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=2)

        ttk.Label(frm, text="Website:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        site_entry = ttk.Entry(frm, width=40)
        site_entry.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(frm, text="Username:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        user_entry = ttk.Entry(frm, width=40)
        user_entry.grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(frm, text="Password:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        pwd_entry = ttk.Entry(frm, show="*", width=40)
        pwd_entry.grid(row=2, column=1, padx=6, pady=6)

        strength_label = ttk.Label(frm, text="", font=("Segoe UI", 10, "bold"))
        strength_label.grid(row=3, column=1, sticky="w", pady=(0,8))

        def on_key(event=None):
            s, color = check_strength(pwd_entry.get())
            strength_label.config(text=f"Strength: {s}" if s else "", foreground=color)

        pwd_entry.bind("<KeyRelease>", on_key)

        def save_pwd():
            site = site_entry.get().strip()
            uname = user_entry.get().strip()
            pwd = pwd_entry.get()
            if not site or not uname or not pwd:
                messagebox.showerror("Error", "All fields are required.")
                return
            enc = vigenere_encrypt(pwd, VIGENERE_KEY)
            vault.setdefault(self.current_user, []).append({"site": site, "username": uname, "password": enc})
            save("vault.json", vault)
            log(f"Added {site} for {self.current_user}")
            self.refresh_table()
            win.destroy()

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text="Save", command=save_pwd).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Cancel", command=win.destroy).grid(row=0, column=1, padx=6)

    # ---- Search ----
    def search_password(self):
        q = simpledialog.askstring("Search", "Enter website to search:", parent=self)
        if not q:
            return
        vault = load("vault.json")
        if self.current_user in vault:
            for entry in vault[self.current_user]:
                if q.lower() in entry["site"].lower():
                    messagebox.showinfo("Found", f"Site: {entry['site']}\nUsername: {entry['username']}\nPassword: {vigenere_decrypt(entry['password'], VIGENERE_KEY)}")
                    return
        messagebox.showinfo("Not found", "No match.")

    # ---- Update ----
    def update_password(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select a row to update.")
            return
        vals = self.tree.item(sel[0], "values")
        site, uname = vals[0], vals[1]

        win = tk.Toplevel(self)
        win.title("Update Password")
        win.resizable(False, False)
        win.grab_set()
        frm = ttk.Frame(win, padding=12, style="Card.TFrame")
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=2)

        ttk.Label(frm, text=f"Update password for {site} ({uname})").grid(row=0, column=0, columnspan=2, pady=(0,8))
        ttk.Label(frm, text="New Password:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        new_entry = ttk.Entry(frm, show="*", width=40)
        new_entry.grid(row=1, column=1, padx=6, pady=6)

        strength_label = ttk.Label(frm, text="", font=("Segoe UI", 10, "bold"))
        strength_label.grid(row=2, column=1, sticky="w", pady=(0,8))

        def on_key(event=None):
            s, color = check_strength(new_entry.get())
            strength_label.config(text=f"Strength: {s}" if s else "", foreground=color)

        new_entry.bind("<KeyRelease>", on_key)

        def do_update():
            new_pwd = new_entry.get()
            if new_pwd is None or new_pwd == "":
                messagebox.showerror("Error", "Password cannot be empty.")
                return
            vault = load("vault.json")
            if self.current_user in vault:
                for entry in vault[self.current_user]:
                    if entry["site"] == site and entry["username"] == uname:
                        entry["password"] = vigenere_encrypt(new_pwd, VIGENERE_KEY)
                        save("vault.json", vault)
                        log(f"Updated {site} for {self.current_user}")
                        self.refresh_table()
                        messagebox.showinfo("Success", "Updated.")
                        win.destroy()
                        return
            messagebox.showerror("Error", "Entry not found.")

        btnf = ttk.Frame(frm)
        btnf.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btnf, text="Update", command=do_update).grid(row=0, column=0, padx=6)
        ttk.Button(btnf, text="Cancel", command=win.destroy).grid(row=0, column=1, padx=6)

    # ---- Delete ----
    def delete_password(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select a row to delete.")
            return
        vals = self.tree.item(sel[0], "values")
        site, uname = vals[0], vals[1]
        if not messagebox.askyesno("Confirm", f"Delete {site} ({uname})?"):
            return
        vault = load("vault.json")
        if self.current_user in vault:
            for entry in list(vault[self.current_user]):
                if entry["site"] == site and entry["username"] == uname:
                    vault[self.current_user].remove(entry)
                    save("vault.json", vault)
                    log(f"Deleted {site} for {self.current_user}")
                    self.refresh_table()
                    messagebox.showinfo("Deleted", f"{site} removed.")
                    return
        messagebox.showerror("Error", "Entry not found.")

    # ---- Logout ----
    def logout(self):
        self.current_user = None
        self.show_main_menu()

# ===== Run =====
if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
