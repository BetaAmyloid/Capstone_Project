import tkinter as tk

def on_button_click():
    print("Button clicked!")
    label.config(text="Button Clicked")

def show_message():
    tk.messagebox.showinfo("Title", "This is a message box")

# Initialize main window
root = tk.Tk()
root.title("My Application")

# Add widgets
label = tk.Label(root, text="Hello, Tkinter!")
label.pack()

button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack()

entry = tk.Entry(root)
entry.pack()

text = tk.Text(root, height=5, width=30)
text.pack()

canvas = tk.Canvas(root, width=200, height=100)
canvas.pack()
canvas.create_line(0, 0, 200, 100)
canvas.create_rectangle(50, 25, 150, 75, fill="blue")

checkbutton_var = tk.IntVar()
checkbutton = tk.Checkbutton(root, text="Check me", variable=checkbutton_var)
checkbutton.pack()

radiobutton_var = tk.IntVar()
radiobutton1 = tk.Radiobutton(root, text="Option 1", variable=radiobutton_var, value=1)
radiobutton2 = tk.Radiobutton(root, text="Option 2", variable=radiobutton_var, value=2)
radiobutton1.pack()
radiobutton2.pack()

scale = tk.Scale(root, from_=0, to=100)
scale.pack()

listbox = tk.Listbox(root)
listbox.insert(1, "Item 1")
listbox.insert(2, "Item 2")
listbox.pack()

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open")
filemenu.add_command(label="Save")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

# Run the application
root.mainloop()
