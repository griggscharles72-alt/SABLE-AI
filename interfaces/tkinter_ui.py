# interfaces/tkinter_ui.py
try:
    import tkinter as tk
except ImportError:
    tk = None

def launch_ui():
    if tk is None:
        return {"error": "Tkinter not available"}
    root = tk.Tk()
    root.title("SABLE-Agent GUI")
    label = tk.Label(root, text="GUI Placeholder")
    label.pack()
    # root.mainloop()  # Commented for testability
    return {"status": "GUI initialized"}

if __name__ == "__main__":
    print(launch_ui())
