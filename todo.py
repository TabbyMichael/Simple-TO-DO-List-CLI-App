import os
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import simpledialog, Toplevel
from PIL import Image, ImageTk  # Import from Pillow to handle image resizing

# File where tasks will be stored
TODO_FILE = "tasks.txt"

def load_tasks():
    """Load tasks from file."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            tasks = f.readlines()
        return [task.strip() for task in tasks]
    return []

def save_tasks(tasks):
    """Save tasks to file."""
    with open(TODO_FILE, "w") as f:
        for task in tasks:
            f.write(f"{task}\n")

def update_task_listbox(tasks_frame, tasks, trash_icon):
    """Update the tasks displayed with checkboxes and delete buttons."""
    for widget in tasks_frame.winfo_children():
        widget.destroy()  # Clear previous task frames

    completed_tasks = sum(1 for task in tasks if task.startswith("[DONE]"))
    task_count = len(tasks)

    # Update progress bar
    progress = (completed_tasks / task_count) * 100 if task_count > 0 else 0
    progress_var.set(progress)
    progress_label.config(text=f"Progress: {completed_tasks}/{task_count} tasks completed")

    for idx, task in enumerate(tasks):
        task_frame = tk.Frame(tasks_frame, bd=1, relief="solid", padx=10, pady=5)
        task_frame.pack(fill="x", pady=5)

        is_done = task.startswith("[DONE]")
        task_text = task.replace("[DONE]", "").strip()

        # Extract priority from task
        priority_color = get_priority_color(task)

        # Checkbox to mark as done
        done_var = tk.BooleanVar(value=is_done)
        checkbox = tk.Checkbutton(task_frame, variable=done_var, command=lambda idx=idx, var=done_var: mark_task_done(idx, var, tasks))
        checkbox.pack(side="left", padx=5)

        # Label for the task text with color based on priority
        task_label = tk.Label(task_frame, text=task_text, anchor="w", bg=priority_color)
        task_label.pack(side="left", fill="x", expand=True)
        task_label.bind("<Button-1>", lambda e, idx=idx: edit_task_popup(idx, tasks))  # Make task label clickable

        # Delete button with resized trash can icon
        delete_button = tk.Button(task_frame, image=trash_icon, command=lambda idx=idx: delete_task(idx, tasks), bd=0)
        delete_button.pack(side="right", padx=5)

def get_priority_color(task):
    """Return the color based on task priority."""
    if "Priority: High" in task:
        return "red"  # High priority
    elif "Priority: Medium" in task:
        return "orange"  # Medium priority
    elif "Priority: Low" in task:
        return "green"  # Low priority
    return "white"  # Default color

def add_task_popup(tasks, tasks_frame, trash_icon):
    """Popup to add a new task."""
    popup = Toplevel()
    popup.title("Add Task")

    # Create a label for task entry
    task_label = tk.Label(popup, text="Task Description:")
    task_label.pack(pady=5)
    
    task_entry = tk.Entry(popup, width=40)  # This is the text field for entering the task
    task_entry.pack(pady=5)

    # Add a dropdown for priority selection
    priority_label = tk.Label(popup, text="Priority:")
    priority_label.pack(pady=5)
    priority_options = ["Low", "Medium", "High"]
    priority_var = tk.StringVar(value="Medium")
    priority_dropdown = ttk.Combobox(popup, textvariable=priority_var, values=priority_options, state="readonly")
    priority_dropdown.pack(pady=5)

    # Add a dropdown for category selection
    category_label = tk.Label(popup, text="Category:")
    category_label.pack(pady=5)
    category_options = ["Work", "Personal", "Shopping", "Health", "Hobbies", "Family", "Education", "Travel", "Finance", "Home"]
    category_var = tk.StringVar(value="Work")
    category_dropdown = ttk.Combobox(popup, textvariable=category_var, values=category_options, state="readonly")
    category_dropdown.pack(pady=5)

    # Add a date picker for setting a deadline
    deadline_label = tk.Label(popup, text="Deadline:")
    deadline_label.pack(pady=5)
    deadline_picker = DateEntry(popup, width=20, background="darkblue", foreground="white", borderwidth=2)
    deadline_picker.pack(pady=5)

    # Save the task with priority, deadline, and category
    save_button = tk.Button(popup, text="Save Task", command=lambda: save_new_task_with_priority(
        task_entry.get(), priority_var.get(), category_var.get(), deadline_picker.get(), tasks, tasks_frame, popup, trash_icon))
    save_button.pack(pady=5)

def save_new_task_with_priority(task_text, priority, category, deadline, tasks, tasks_frame, popup, trash_icon):
    """Save a new task with priority, category, and deadline and update the listbox."""
    task = f"{task_text} (Priority: {priority}, Category: {category}, Deadline: {deadline})"
    if task_text.strip():
        tasks.append(task)
        save_tasks(tasks)
        update_task_listbox(tasks_frame, tasks, trash_icon)
    popup.destroy() 

def search_tasks(query, tasks_frame, trash_icon):
    """Search for tasks that match the query and update the task list."""
    filtered_tasks = [task for task in load_tasks() if query.lower() in task.lower()]
    update_task_listbox(tasks_frame, filtered_tasks, trash_icon)

def toggle_dark_mode():
    """Toggle dark mode on and off."""
    if root["bg"] == "white":
        root.config(bg="black")
        tasks_frame.config(bg="black")
        progress_frame.config(bg="black")
        search_frame.config(bg="black")
    else:
        root.config(bg="white")
        tasks_frame.config(bg="white")
        progress_frame.config(bg="white")
        search_frame.config(bg="white")

def edit_task_popup(task_idx, tasks):
    """Popup to edit an existing task."""
    popup = Toplevel()
    popup.title("Edit Task")

    current_task = tasks[task_idx].replace("[DONE]", "").strip()

    task_entry = tk.Entry(popup, width=40)
    task_entry.insert(0, current_task)
    task_entry.pack(pady=10, padx=10)

    save_button = tk.Button(popup, text="Save Changes", command=lambda: save_edited_task(task_idx, task_entry.get(), tasks, popup))
    save_button.pack(pady=5)

def save_edited_task(task_idx, new_task, tasks, popup):
    """Save the edited task and update the listbox."""
    if new_task.strip():
        tasks[task_idx] = new_task.strip()
        save_tasks(tasks)
        update_task_listbox(tasks_frame, tasks, trash_icon)
    popup.destroy()  # Close the popup after saving

def delete_task(task_idx, tasks):
    """Delete a task from the list."""
    tasks.pop(task_idx)
    save_tasks(tasks)
    update_task_listbox(tasks_frame, tasks, trash_icon)

def mark_task_done(task_idx, done_var, tasks):
    """Mark a task as done or not done."""
    if done_var.get():
        tasks[task_idx] = f"[DONE] {tasks[task_idx].replace('[DONE]', '').strip()}"
    else:
        tasks[task_idx] = tasks[task_idx].replace("[DONE]", "").strip()
    save_tasks(tasks)
    update_task_listbox(tasks_frame, tasks, trash_icon)

def main():
    global root, tasks_frame, trash_icon, progress_var, progress_label, progress_frame, search_frame  # Make elements accessible

    # Load tasks
    tasks = load_tasks()

    # Create the main window
    root = tk.Tk()
    root.title("To-Do App")
    root.config(bg="white")  # Light mode by default

    # Load and resize the trash icon using Pillow
    trash_img = Image.open("trash_can.png")  # Load the trash can image
    trash_img = trash_img.resize((20, 20), Image.Resampling.LANCZOS)  # Resize the image to 20x20 pixels
    trash_icon = ImageTk.PhotoImage(trash_img)  # Convert to PhotoImage for tkinter

    # Create the search bar
    search_frame = tk.Frame(root, bg="white")
    search_frame.pack(pady=5)
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=10)
    search_button = tk.Button(search_frame, text="Search", command=lambda: search_tasks(search_entry.get(), tasks_frame, trash_icon))
    search_button.pack(side="left", padx=5)

    # Button to add new tasks (instead of an entry field)
    add_task_button = tk.Button(root, text="+ Add Task", command=lambda: add_task_popup(tasks, tasks_frame, trash_icon))
    add_task_button.pack(pady=10)

    # Progress bar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(fill="x", padx=10)

    progress_frame = tk.Frame(root, bg="white")
    progress_frame.pack(pady=5)
    progress_label = tk.Label(progress_frame, text="Progress: 0/0 tasks completed", bg="white")
    progress_label.pack()

    # Frame to hold tasks
    tasks_frame = tk.Frame(root, bg="white")
    tasks_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Update the task listbox with loaded tasks
    update_task_listbox(tasks_frame, tasks, trash_icon)

    # Button to toggle dark mode
    dark_mode_button = tk.Button(root, text="Toggle Dark Mode", command=toggle_dark_mode)
    dark_mode_button.pack(pady=10)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
