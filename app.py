import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, simpledialog
import subprocess
import os
import importlib.util
import webbrowser
import json  # For JSON file handling

# Path to scripts.txt
scripts_txt_path = os.path.join(os.path.dirname(__file__), "scripts_folder" 
"")

# Data files for persistent storage
DATA_FILES = {
    "scripts": os.path.join(os.path.dirname(__file__), "scripts_data.json"),
    "cmds": os.path.join(os.path.dirname(__file__), "cmds_data.json")
}

class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TSE Dashboard")
        self.geometry("800x600")

        # --- Helpful Links Frame (Scrollable & Dynamic) ---
        links_frame = tk.LabelFrame(self, text="Helpful Links", padx=10, pady=10)
        links_frame.pack(fill="x", padx=10, pady=5)

        # Canvas + Scrollbar for links
        canvas = tk.Canvas(links_frame, height=120)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(links_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.links_inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.links_inner_frame, anchor="nw")

        self.links = [
            {"desc": "Playbook for SQL scripts", "url": "https://your-playbook-link.com"},
            {"desc": "Company Wiki", "url": "https://your-company-wiki.com"},
            {"desc": "Troubleshooting Guide", "url": "https://your-troubleshooting-guide.com"},
        ]

        # Listbox for selecting links to delete
        self.links_listbox = tk.Listbox(self.links_inner_frame, height=6)
        self.links_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        self.links_inner_frame.grid_rowconfigure(0, weight=1)
        self.links_inner_frame.grid_columnconfigure(0, weight=1)

        self.render_links()

        # Add/Delete buttons
        add_btn = tk.Button(links_frame, text="Add Link", command=self.add_link)
        add_btn.pack(side="left", padx=5)
        # del_btn = tk.Button(links_frame, text="Delete Link", command=self.delete_link)
        # del_btn.pack(side="left", padx=5)

        # Update scroll region when links change
        self.links_inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # --- Scripts Frame ---
        script_frame = tk.LabelFrame(self, text="Scripts", padx=10, pady=10)
        script_frame.pack(fill="x", padx=10, pady=5)
        self.scripts_frame = script_frame  # Optional, for reference

        self.scripts_list_frame = tk.Frame(script_frame)
        self.scripts_list_frame.pack(fill="x", side="left", expand=True)

        self.scripts = []
        scripts_folder = os.path.join(os.path.dirname(__file__), "scripts_folder")
        if os.path.exists(scripts_folder):
            for filename in os.listdir(scripts_folder):
                if filename.endswith(".txt"):
                    self.scripts.append({"desc": filename, "filename": filename})

        self.render_scripts(script_frame, scripts_folder)

        script_btn_frame = tk.Frame(script_frame)
        script_btn_frame.pack(side="right", padx=10, pady=5)

        new_script_btn = tk.Button(script_btn_frame, text="New Script File", command=lambda: self.create_new_script_file(scripts_folder))
        new_script_btn.pack(fill="x", pady=2)
        refresh_script_btn = tk.Button(script_btn_frame, text="Refresh", command=lambda: self.refresh_scripts(scripts_folder))
        refresh_script_btn.pack(fill="x", pady=2)

        # --- CMDs Frame ---
        cmds_frame = tk.LabelFrame(self, text="Saved CMDs", padx=10, pady=10)
        cmds_frame.pack(fill="x", padx=10, pady=5)
        self.cmds_frame = cmds_frame  # <-- Add this line
        self.cmds_list_frame = tk.Frame(cmds_frame)
        self.cmds_list_frame.pack(fill="x", side="left", expand=True)

        self.cmds = []
        cmds_folder = os.path.join(os.path.dirname(__file__), "cmds_folder")
        if os.path.exists(cmds_folder):
            for filename in os.listdir(cmds_folder):
                if filename.endswith(".txt"):
                    self.cmds.append({"desc": "No description", "filename": filename})

        self.render_cmds(cmds_frame, cmds_folder)

        cmd_btn_frame = tk.Frame(cmds_frame)
        cmd_btn_frame.pack(side="right", padx=10, pady=5)

        add_cmd_btn = tk.Button(cmd_btn_frame, text="New CMD File", command=lambda: self.create_new_cmd_file(cmds_folder))
        add_cmd_btn.pack(fill="x", pady=2)
        refresh_cmd_btn = tk.Button(cmd_btn_frame, text="Refresh", command=lambda: self.refresh_cmds(cmds_folder))
        refresh_cmd_btn.pack(fill="x", pady=2)

        # Notes Frame
        notes_frame = tk.LabelFrame(self, text="Notes", padx=10, pady=10)
        notes_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.notes_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD, height=10)
        self.notes_text.pack(fill="both", expand=True)

        self.notes_save_folder = os.path.join(os.path.expanduser("~"), "Desktop")

        select_folder_btn = tk.Button(notes_frame, text="Select Folder", command=self.select_notes_folder)
        select_folder_btn.pack(side="left", fill="x", padx=5, pady=5)

        save_notes_btn = tk.Button(notes_frame, text="Save Notes", command=self.save_notes)
        save_notes_btn.pack(side="right", fill="x", padx=5, pady=5)

       
        # # Command Prompts Listbox (OLD, REMOVE THIS)
        # cmds_frame = tk.LabelFrame(self, text="Saved CMDs", padx=10, pady=10)
        # cmds_frame.pack(fill="x", padx=10, pady=5)

        # self.cmds_listbox = tk.Listbox(cmds_frame, height=5)
        # self.cmds_listbox.pack(side="left", fill="both", expand=True)
        # cmds_scroll = tk.Scrollbar(cmds_frame, command=self.cmds_listbox.yview)
        # cmds_scroll.pack(side="right", fill="y")
        # self.cmds_listbox.config(yscrollcommand=cmds_scroll.set)

        # # Load command txt files from cmds_folder
        # cmds_folder = os.path.join(os.path.dirname(__file__), "cmds_folder")
        # self.cmds = [
        #     {"desc": "Who am I", "filename": "whoami.txt"},
        #     # ...
        # ]
        # if os.path.exists(cmds_folder):
        #     for filename in os.listdir(cmds_folder):
        #         if filename.endswith(".txt"):
        #             self.cmds_listbox.insert(tk.END, filename)
        # else:
        #     print(f"CMDs folder not found: {cmds_folder}")

        # show_cmd_btn = tk.Button(cmds_frame, text="Show Command", command=self.show_selected_cmd)
        # show_cmd_btn.pack(side="bottom", fill="x", pady=5)

        # refresh_cmds_btn = tk.Button(cmds_frame, text="Refresh Commands", command=self.refresh_cmds)
        # refresh_cmds_btn.pack(side="bottom", fill="x", pady=5)

    def load_script(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.script_listbox.insert(tk.END, file_path)

    def run_script(self):
        selected = self.script_listbox.curselection()
        if selected:
            script_path = self.script_listbox.get(selected[0])
            try:
                exec(open(script_path).read(), {})
                messagebox.showinfo("Success", f"Ran {script_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def select_notes_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.notes_save_folder = folder
            messagebox.showinfo("Folder Selected", f"Notes will be saved to:\n{folder}")

    def save_notes(self):
        notes = self.notes_text.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(initialdir=self.notes_save_folder, defaultextension=".txt")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(notes)
            messagebox.showinfo("Saved", f"Notes saved to:\n{file_path}")
            self.notes_text.delete("1.0", tk.END)  # Clear notes after saving

    def run_command(self):
        cmd = self.command_entry.get()
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            messagebox.showinfo("Command Output", output)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Command Error", e.output)

    def show_scripts_txt(self):
        # Show the contents of scripts.txt in a popup window for copy/paste
        try:
            with open(scripts_txt_path, "r") as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading scripts.txt: {e}"

        popup = tk.Toplevel(self)
        popup.title("scripts.txt Content")
        popup.geometry("500x300")
        text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(tk.END, content)
        text_widget.config(state="normal")

    def show_selected_script(self):
        selected = self.script_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a script from the list.")
            return
        filename = self.script_listbox.get(selected[0])
        scripts_folder = os.path.join(os.path.dirname(__file__), "scripts_folder")
        script_path = os.path.join(scripts_folder, filename)
        print(f"Trying to open: {script_path}")  # Debug: print file path
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"File content:\n{content}")  # Debug: print file content
        except Exception as e:
            content = f"Error loading {script_path}: {e}"

        popup = tk.Toplevel(self)
        popup.title(f"Script: {filename}")
        popup.geometry("500x300")
        text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(tk.END, content)
        text_widget.config(state="normal")  # Editable for copy/paste

        def save_changes():
            content = text_widget.get("1.0", tk.END)
            try:
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(content)
                  
                
                messagebox.showinfo("Saved", f"{filename} saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {e}")

        save_btn = tk.Button(popup, text="Save", command=save_changes)
        save_btn.pack(side="bottom", fill="x", pady=5)

    def show_selected_cmd(self):
        selected = self.cmds_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a command from the list.")
            return
        filename = self.cmds_listbox.get(selected[0])
        cmds_folder = os.path.join(os.path.dirname(__file__), "cmds_folder")
        cmd_path = os.path.join(cmds_folder, filename)
        print(f"Trying to open: {cmd_path}")  # Debug: print file path
        try:
            with open(cmd_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"File content:\n{content}")  # Debug: print file content
        except Exception as e:
            content = f"Error loading {cmd_path}: {e}"

        popup = tk.Toplevel(self)
        popup.title(f"Command: {filename}")
        popup.geometry("500x300")
        text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(tk.END, content)
        text_widget.config(state="normal")  # Editable for copy/paste

        def save_changes():
            content = text_widget.get("1.0", tk.END)
            try:
                with open(cmd_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(content)
                  
                
                messagebox.showinfo("Saved", f"{filename} saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {e}")

        save_btn = tk.Button(popup, text="Save", command=save_changes)
        save_btn.pack(side="bottom", fill="x", pady=5)

    def refresh_scripts(self, folder):
        scripts_dict = {s["filename"]: s["desc"] for s in self.scripts}
        self.scripts.clear()
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith(".txt"):
                    desc = scripts_dict.get(filename, filename)
                    self.scripts.append({"desc": desc, "filename": filename})
        self.render_scripts(self.scripts_frame, folder)

    def refresh_cmds(self, folder):
        cmds_dict = {c["filename"]: c["desc"] for c in self.cmds}
        self.cmds.clear()
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith(".txt"):
                    desc = cmds_dict.get(filename, "No description")
                    self.cmds.append({"desc": desc, "filename": filename})
        self.render_cmds(self.cmds_frame, folder)

    def render_links(self):
        # Clear previous widgets
        for widget in self.links_inner_frame.winfo_children():
            widget.destroy()
        for idx, link in enumerate(self.links):
            desc_label = tk.Label(self.links_inner_frame, text=link["desc"] + ": ", anchor="w")
            desc_label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            url_label = tk.Label(self.links_inner_frame, text=link["url"], fg="blue", cursor="hand2", anchor="w")
            url_label.grid(row=idx, column=1, sticky="w", padx=5)
            url_label.bind("<Button-1>", lambda e, url=link["url"]: webbrowser.open_new(url))
            edit_btn = tk.Button(self.links_inner_frame, text="Edit", command=lambda i=idx: self.edit_link(i))
            edit_btn.grid(row=idx, column=2, padx=5)
            del_btn = tk.Button(self.links_inner_frame, text="Delete", command=lambda i=idx: self.delete_link(i))
            del_btn.grid(row=idx, column=3, padx=5)

    def add_link(self):
        desc = simpledialog.askstring("Add Link", "Enter description:", parent=self)
        url = simpledialog.askstring("Add Link", "Enter URL:", parent=self)
        if desc and url:
            self.links.append({"desc": desc, "url": url})
            self.render_links()

    def delete_link(self, idx=None):
        if idx is not None:
            del self.links[idx]
            self.render_links()
        else:
            selected = self.links_listbox.curselection()
            if not selected:
                messagebox.showinfo("Delete Link", "Please select a link to delete.")
                return
            idx = selected[0]
            del self.links[idx]
            self.render_links()
  
    def edit_link(self, idx):
        link = self.links[idx]
        new_desc = simpledialog.askstring("Edit Link", "Edit description:", initialvalue=link["desc"], parent=self)
        new_url = simpledialog.askstring("Edit Link", "Edit URL:", initialvalue=link["url"], parent=self)
        if new_desc and new_url:
            self.links[idx] = {"desc": new_desc, "url": new_url}
            self.render_links()
  
    def render_scripts(self, parent, scripts_folder):
        # Only clear the list frame, not the button frame
        for widget in self.scripts_list_frame.winfo_children():
            widget.destroy()
        for idx, script in enumerate(self.scripts):
            desc_label = tk.Label(self.scripts_list_frame, text=script["desc"] + ": ", anchor="w")
            desc_label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            file_label = tk.Label(self.scripts_list_frame, text=script["filename"], fg="blue", cursor="hand2", anchor="w")
            file_label.grid(row=idx, column=1, sticky="w", padx=5)
            file_label.bind("<Button-1>", lambda e, f=script["filename"]: self.show_script_content(scripts_folder, f))
            edit_btn = tk.Button(self.scripts_list_frame, text="Edit", command=lambda i=idx: self.edit_script(i))
            edit_btn.grid(row=idx, column=2, padx=5)
            del_btn = tk.Button(self.scripts_list_frame, text="Delete", command=lambda i=idx: self.delete_script(i))
            del_btn.grid(row=idx, column=3, padx=5)

    def show_script_content(self, folder, filename):
        path = os.path.join(folder, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading {path}: {e}"
        popup = tk.Toplevel(self)
        popup.title(f"Script: {filename}")
        popup.geometry("500x300")
        text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(tk.END, content)
        text_widget.config(state="normal")

    def add_script(self, folder):
        desc = simpledialog.askstring("Add Script", "Enter description:", parent=self)
        filename = simpledialog.askstring("Add Script", "Enter filename (must exist in folder):", parent=self)
        if desc and filename and os.path.exists(os.path.join(folder, filename)):
            self.scripts.append({"desc": desc, "filename": filename})
            self.render_scripts(self.scripts_frame, folder)

    def create_new_script_file(self, folder):
        filename = simpledialog.askstring("New Script", "Enter new script filename (e.g. script4.txt):", parent=self)
        if not filename or not filename.endswith(".txt"):
            return
        content = simpledialog.askstring("New Script", "Enter initial content for the script:", parent=self)
        if filename and content is not None:
            path = os.path.join(folder, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            desc = simpledialog.askstring("New Script", "Enter description for the script:", parent=self)
            if not desc:
                desc = filename
            # Add to self.scripts
            self.scripts.append({"desc": desc, "filename": filename})
            # Refresh from folder to ensure UI matches files
            self.refresh_scripts(folder)

    def create_new_cmd_file(self, folder):
        filename = simpledialog.askstring("New CMD", "Enter new CMD filename (e.g. cmd4.txt):", parent=self)
        if not filename or not filename.endswith(".txt"):
            return
        content = simpledialog.askstring("New CMD", "Enter initial content for the CMD:", parent=self)
        if filename and content is not None:
            path = os.path.join(folder, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            desc = simpledialog.askstring("New CMD", "Enter description for the CMD:", parent=self)
            if not desc:
                desc = "No description"
            self.cmds.append({"desc": desc, "filename": filename})
            self.refresh_cmds(folder)

    def edit_script(self, idx):
        script = self.scripts[idx]
        folder = os.path.join(os.path.dirname(__file__), "scripts_folder")
        file_path = os.path.join(folder, script["filename"])

        # Load current file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()
        except Exception as e:
            current_content = f"Error loading file: {e}"

        # Popup for editing file content
        popup = tk.Toplevel(self)
        popup.title(f"Edit Script: {script['filename']}")
        popup.geometry("400x400")  # Approx 100x100 px for text area

        # Frame for description and content
        edit_frame = tk.Frame(popup)
        edit_frame.pack(fill="both", expand=True, padx=10, pady=10)

        desc_label = tk.Label(edit_frame, text="Description:")
        desc_label.pack(anchor="w")
        desc_entry = tk.Entry(edit_frame, width=50)
        desc_entry.pack(fill="x", padx=5, pady=5)
        desc_entry.insert(0, script["desc"])

        content_label = tk.Label(edit_frame, text="Content:")
        content_label.pack(anchor="w")
        text_widget = tk.Text(edit_frame, wrap=tk.WORD, width=50, height=10)
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, current_content)

        def save_changes():
            updated_content = text_widget.get("1.0", tk.END)
            new_desc = desc_entry.get()
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                # Update in self.scripts
                script["desc"] = new_desc
                self.refresh_scripts(folder)
                popup.destroy()
                messagebox.showinfo("Saved", f"{script['filename']} updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {e}")

        save_btn = tk.Button(popup, text="Save", command=save_changes)
        save_btn.pack(side="bottom", fill="x", pady=5)

    def delete_script(self, idx):
        script = self.scripts[idx]
        folder = os.path.join(os.path.dirname(__file__), "scripts_folder")
        file_path = os.path.join(folder, script["filename"])
        # Remove from disk if file exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")
        # Remove from list and refresh UI
        del self.scripts[idx]
        self.refresh_scripts(folder)

    def render_cmds(self, parent, cmds_folder):
        for widget in self.cmds_list_frame.winfo_children():
            widget.destroy()
        for idx, cmd in enumerate(self.cmds):
            desc_label = tk.Label(self.cmds_list_frame, text=cmd["desc"] + ": ", anchor="w")
            desc_label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            file_label = tk.Label(self.cmds_list_frame, text=cmd["filename"], fg="blue", cursor="hand2", anchor="w")
            file_label.grid(row=idx, column=1, sticky="w", padx=5)
            file_label.bind("<Button-1>", lambda e, f=cmd["filename"]: self.show_cmd_content(cmds_folder, f))
            edit_btn = tk.Button(self.cmds_list_frame, text="Edit", command=lambda i=idx: self.edit_cmd(i))
            edit_btn.grid(row=idx, column=2, padx=5)
            del_btn = tk.Button(self.cmds_list_frame, text="Delete", command=lambda i=idx: self.delete_cmd(i))
            del_btn.grid(row=idx, column=3, padx=5)

    def show_cmd_content(self, folder, filename):
        path = os.path.join(folder, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading {path}: {e}"
        popup = tk.Toplevel(self)
        popup.title(f"CMD: {filename}")
        popup.geometry("500x300")
        text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(tk.END, content)
        text_widget.config(state="normal")

    def add_cmd(self, folder):
        desc = simpledialog.askstring("Add CMD", "Enter description:", parent=self)
        filename = simpledialog.askstring("Add CMD", "Enter filename (must exist in folder):", parent=self)
        if desc and filename and os.path.exists(os.path.join(folder, filename)):
            self.cmds.append({"desc": desc, "filename": filename})
            self.render_cmds(self.cmds_frame, folder)

    def edit_cmd(self, idx):
        cmd = self.cmds[idx]
        folder = os.path.join(os.path.dirname(__file__), "cmds_folder")
        file_path = os.path.join(folder, cmd["filename"])

        # Load current file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()
        except Exception as e:
            current_content = f"Error loading file: {e}"

        # Popup for editing file content (text area 100x100 px)
        popup = tk.Toplevel(self)
        popup.title(f"Edit CMD: {cmd['filename']}")
        popup.geometry("400x400")  # Approx 100x100 px for text area

        # Frame for description and content
        edit_frame = tk.Frame(popup)
        edit_frame.pack(fill="both", expand=True, padx=10, pady=10)

        desc_label = tk.Label(edit_frame, text="Description:")
        desc_label.pack(anchor="w")
        desc_entry = tk.Entry(edit_frame, width=50)
        desc_entry.pack(fill="x", padx=5, pady=5)
        desc_entry.insert(0, cmd["desc"])

        content_label = tk.Label(edit_frame, text="Content:")
        content_label.pack(anchor="w")
        text_widget = tk.Text(edit_frame, wrap=tk.WORD, width=50, height=10)
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, current_content)

        def save_changes():
            updated_content = text_widget.get("1.0", tk.END)
            new_desc = desc_entry.get()
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                # Update in self.cmds
                cmd["desc"] = new_desc
                self.refresh_cmds(folder)
                popup.destroy()
                messagebox.showinfo("Saved", f"{cmd['filename']} updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {e}")

        save_btn = tk.Button(popup, text="Save", command=save_changes)
        save_btn.pack(side="bottom", fill="x", pady=5)

    def delete_cmd(self, idx):
        cmd = self.cmds[idx]
        folder = os.path.join(os.path.dirname(__file__), "cmds_folder")
        file_path = os.path.join(folder, cmd["filename"])
        # Remove from disk if file exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")
        # Remove from list and refresh UI
        del self.cmds[idx]
        self.refresh_cmds(folder)

    def load_data(self):
        """Load scripts and cmds data from JSON files."""
        for key, file_path in DATA_FILES.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        if key == "scripts":
                            self.scripts = data
                            scripts_folder = os.path.join(os.path.dirname(__file__), "scripts_folder")
                            self.render_scripts(self.scripts_frame, scripts_folder)
                        elif key == "cmds":
                            self.cmds = data
                            cmds_folder = os.path.join(os.path.dirname(__file__), "cmds_folder")
                            self.render_cmds(self.cmds_frame, cmds_folder)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not load {key} data: {e}")

    def save_data(self):
        """Save scripts and cmds data to JSON files."""
        for key, file_path in DATA_FILES.items():
            try:
                data = self.scripts if key == "scripts" else self.cmds
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save {key} data: {e}")


if __name__ == "__main__":
    app = DashboardApp()
    app.load_data()  # Load data at startup
    app.mainloop()
    app.save_data()  # Save data on exit