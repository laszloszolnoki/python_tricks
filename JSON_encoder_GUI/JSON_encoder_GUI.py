import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import json
from secure_json_encoder import SecureJsonEncoder
import shutil

class JsonEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure JSON Editor")

        # Apply 'clam' style
        style = ttk.Style()
        style.theme_use('clam')

        # Make the main window 50% wider
        window_width = int(root.winfo_screenwidth() * 0.75)
        window_height = int(root.winfo_screenheight() * 0.5)
        root.geometry(f"{window_width}x{window_height}")

        self.encoder = SecureJsonEncoder()

        self.text_area = tk.Text(root, wrap='word', undo=True)
        self.text_area.pack(expand=1, fill='both')

        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        # New File menu
        new_file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_command(label="New", command=self.new_file)

        # File operations menus
        open_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Open", menu=open_menu)
        open_menu.add_command(label="With GIF", command=self.open_file_with_gif)
        open_menu.add_command(label="With Password", command=self.open_file_with_password)

        save_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Save", menu=save_menu)
        save_menu.add_command(label="With GIF", command=self.save_file_with_gif)
        save_menu.add_command(label="With Password", command=self.save_file_with_password)

        save_as_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Save As", menu=save_as_menu)
        save_as_menu.add_command(label="With GIF", command=self.save_as_file_with_gif)
        save_as_menu.add_command(label="With Password", command=self.save_as_file_with_password)

        # Add Search menu
        search_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Search", menu=search_menu)
        search_menu.add_command(label="Search (Ctrl+F)", command=self.open_search_dialog)
        search_menu.add_command(label="Search and Replace (Ctrl+R)", command=self.open_search_replace_dialog)

        # Add Edit menu
        edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo (Ctrl+Z)", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo (Ctrl+Y)", command=self.text_area.edit_redo)

        self.current_file_path = None

        # Footer section to display the filename
        self.footer_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.footer_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind Ctrl+F and Ctrl+R
        root.bind('<Control-f>', self.open_search_dialog)
        root.bind('<Control-r>', self.open_search_replace_dialog)

        # Add Ctrl+Z and Ctrl+Y bindings
        root.bind('<Control-z>', lambda e: self.text_area.edit_undo())
        root.bind('<Control-y>', lambda e: self.text_area.edit_redo())
    
    def new_file(self):
        json_content = """{
    "key": "value"
}"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, json_content)
        self.current_file_path = None
    
    def open_file(self, method):
        file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
        if file_path:
            try:
                if method == "gif":
                    gif_key_path = self.get_gif_key_path()
                    if gif_key_path:
                        decrypted_data = self.encoder.decrypt_json(input_file=file_path, gif_key_path=gif_key_path)
                elif method == "password":
                    password = self.get_password()
                    if password:
                        decrypted_data = self.encoder.decrypt_json(input_file=file_path, password=password)
                else:
                    raise ValueError("Invalid method")
                
                if isinstance(decrypted_data, dict):
                    json_content = json.dumps(decrypted_data, indent=4)
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, json_content)
                    self.current_file_path = file_path  # Store the current file path
                    self.footer_label.config(text=f"Current File: {file_path}")  # Update footer with filename
                else:
                    raise ValueError(decrypted_data)  # Raise an error if the returned data is not a JSON object
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def open_file_with_gif(self):
        self.open_file(method="gif")

    def open_file_with_password(self):
        self.open_file(method="password")

    def save_file(self, method, save_as=False):
        if save_as or not self.current_file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary Files", "*.bin")])
        else:
            file_path = self.current_file_path

        if file_path:
            try:
                json_content = self.text_area.get(1.0, tk.END).strip()
                data = json.loads(json_content)  # Validate JSON
                
                # Create a backup of the current file
                backup_file_path = file_path + '.backup'
                try:
                    shutil.copy(file_path, backup_file_path)
                except: # File doesn't exist yet, nothing to backup
                    pass
                
                if method == "gif":
                    gif_key_path = self.get_gif_key_path()
                    if gif_key_path:
                        self.encoder.encrypt_json(data=data, output_file=file_path, gif_key_path=gif_key_path)
                        messagebox.showinfo("Success", "File saved successfully.")
                elif method == "password":
                    password = self.get_password_twice()
                    if password:
                        self.encoder.encrypt_json(data=data, output_file=file_path, password=password)
                        messagebox.showinfo("Success", "File saved successfully.")
                self.current_file_path = file_path  # Update the current file path
                self.footer_label.config(text=f"Current File: {file_path}")  # Update footer with filename
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON content.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            messagebox.showerror("Error", "No file is currently open.")

    def save_file_with_gif(self):
        self.save_file(method="gif")

    def save_file_with_password(self):
        self.save_file(method="password")

    def save_as_file_with_gif(self):
        self.save_file(method="gif", save_as=True)

    def save_as_file_with_password(self):
        self.save_file(method="password", save_as=True)

    def get_gif_key_path(self):
        file_path = filedialog.askopenfilename(title="Select GIF Key File", filetypes=[("GIF Files", "*.gif")])
        
        if file_path:
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("GIF Preview")
            
            try:
                # Load and display the GIF
                gif_image = tk.PhotoImage(file=file_path)
                
                # Scale the image if it's too large
                max_size = 400
                width = gif_image.width()
                height = gif_image.height()
                
                if width > max_size or height > max_size:
                    scale = max_size / max(width, height)
                    width = int(width * scale)
                    height = int(height * scale)
                    gif_image = gif_image.subsample(int(1/scale))
                
                # Create and pack the image label
                image_label = tk.Label(preview_window, image=gif_image)
                image_label.image = gif_image  # Keep a reference to prevent garbage collection
                image_label.pack(padx=10, pady=10)
                
                # Add file path label
                path_label = tk.Label(preview_window, text=f"File: {file_path}")
                path_label.pack(padx=10, pady=(0, 10))
                
                # Add confirmation buttons
                button_frame = tk.Frame(preview_window)
                button_frame.pack(pady=10)
                
                def confirm():
                    preview_window.destroy()
                    self.selected_gif_path = file_path
                
                def cancel():
                    preview_window.destroy()
                    self.selected_gif_path = None
                
                tk.Button(button_frame, text="Confirm", command=confirm).pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
                
                # Make the window modal
                preview_window.transient(self.root)
                preview_window.grab_set()
                self.root.wait_window(preview_window)
                
                return getattr(self, 'selected_gif_path', None)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load GIF preview: {e}")
                preview_window.destroy()
                return None
        
        return None

    def get_password(self):
        password_window = tk.Toplevel(self.root)
        password_window.title("Enter Password")
        
        tk.Label(password_window, text="Password:").pack(pady=5)
        
        password_entry = tk.Entry(password_window, show="*")
        password_entry.pack(pady=5)
        
        def submit_password():
            self.password = password_entry.get()
            password_window.destroy()
        
        tk.Button(password_window, text="Submit", command=submit_password).pack(pady=5)
        
        password_window.transient(self.root)
        password_window.grab_set()
        self.root.wait_window(password_window)
        
        return getattr(self, 'password', None)

    def get_password_twice(self):
        password_window = tk.Toplevel(self.root)
        password_window.title("Enter Password Twice")
        
        tk.Label(password_window, text="Password:").pack(pady=5)
        password_entry1 = tk.Entry(password_window, show="*")
        password_entry1.pack(pady=5)
        
        tk.Label(password_window, text="Confirm Password:").pack(pady=5)
        password_entry2 = tk.Entry(password_window, show="*")
        password_entry2.pack(pady=5)
        
        def submit_password():
            if password_entry1.get() == password_entry2.get():
                self.password = password_entry1.get()
                password_window.destroy()
            else:
                messagebox.showerror("Error", "Passwords do not match.")
        
        tk.Button(password_window, text="Submit", command=submit_password).pack(pady=5)
        
        password_window.transient(self.root)
        password_window.grab_set()
        self.root.wait_window(password_window)
        
        return getattr(self, 'password', None)

    def open_search_dialog(self, event=None):
        search_term = simpledialog.askstring("Search", "Enter search term:")
        if search_term:
            self.search_text(search_term)

    def open_search_replace_dialog(self, event=None):
        dialog = SearchReplaceDialog(self.root, self)
        self.root.wait_window(dialog.top)

    def search_text(self, search_term):
        start_pos = '1.0'
        while True:
            start_pos = self.text_area.search(search_term, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.text_area.tag_add('highlight', start_pos, end_pos)
            self.text_area.tag_config('highlight', background='yellow')
            start_pos = end_pos

    def replace_text(self, search_term, replace_term):
        content = self.text_area.get(1.0, tk.END)
        new_content = content.replace(search_term, replace_term)
        
        # Validate the new content is valid JSON before replacing
        try:
            # Strip whitespace and validate
            new_content = new_content.strip()
            json.loads(new_content)
            
            # If valid, update the text area
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, new_content)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "The replacement would result in invalid JSON content.")

class SearchReplaceDialog:
    def __init__(self, parent, app):
        top = self.top = tk.Toplevel(parent)
        self.app = app
        self.top.title("Search and Replace")

        tk.Label(top, text="Search for:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = tk.Entry(top)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Replace with:").grid(row=1, column=0, sticky=tk.W)
        self.replace_entry = tk.Entry(top)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(top, text="Replace", command=self.replace).grid(row=2, column=0, columnspan=2, pady=5)

    def replace(self):
        search_text = self.search_entry.get()
        replace_text = self.replace_entry.get()
        self.app.replace_text(search_text, replace_text)
        self.top.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonEditorApp(root)
    root.mainloop()
